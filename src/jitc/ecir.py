from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

from .model import (
    AdmissionPolicy,
    ClaimSpec,
    EpistemicObject,
    ObjectKind,
    Permission,
    TaskContract,
)
from .repository import CommandSpec
from .runtime import EpistemicRuntime, JITCError


class ECIRError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ECIRDocument:
    version: str
    contract: TaskContract
    policies: tuple[AdmissionPolicy, ...]
    objects: tuple[EpistemicObject, ...]
    claims: tuple[ClaimSpec, ...]
    commands: tuple[CommandSpec, ...]

    def instantiate_runtime(self) -> EpistemicRuntime:
        runtime = EpistemicRuntime(self.contract)
        for policy in self.policies:
            runtime.register_policy(policy)
        for obj in self.objects:
            runtime.declare_object(obj)
        for claim in self.claims:
            runtime.propose_claim(claim)
        return runtime


def load_ecir(path: Path) -> ECIRDocument:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ECIRError(f"cannot load ECIR document: {exc}") from exc
    if not isinstance(raw, dict):
        raise ECIRError("ECIR document must be a JSON object")
    return parse_ecir(raw)


def parse_ecir(raw: dict[str, Any]) -> ECIRDocument:
    _reject_unknown(
        raw,
        {
            "$schema",
            "ecir_version",
            "contract",
            "policies",
            "objects",
            "claims",
            "commands",
            "permissions",
        },
        "document",
    )
    version = _text(raw, "ecir_version")
    if version != "0.1":
        raise ECIRError(f"unsupported ECIR version: {version}")

    commands = tuple(
        _parse_command(_dict_value(row, "command"))
        for row in _list(raw, "commands")
    )
    command_by_id = _unique_by(
        commands, lambda command: command.command_id, "command_id"
    )

    permissions: list[Permission] = []
    for item in _list(raw, "permissions"):
        row = _dict_value(item, "permission")
        _reject_unknown(row, {"effect", "command_id"}, "permission")
        effect = _text(row, "effect")
        command_id = _text(row, "command_id")
        if effect != "execute":
            raise ECIRError("ECIR v0.1 command permissions require effect=execute")
        if command_id not in command_by_id:
            raise ECIRError(f"permission refers to unknown command: {command_id}")
        permissions.append(
            Permission(effect="execute", resource=command_by_id[command_id].resource_id)
        )

    contract_row = _dict_value(raw.get("contract"), "contract")
    _reject_unknown(
        contract_row, {"contract_id", "mandatory_claim_ids"}, "contract"
    )
    contract = TaskContract(
        contract_id=_text(contract_row, "contract_id"),
        mandatory_claim_ids=_text_tuple(contract_row, "mandatory_claim_ids"),
        permissions=tuple(permissions),
    )

    policies = tuple(
        _parse_policy(_dict_value(row, "policy"))
        for row in _list(raw, "policies")
    )
    objects = tuple(
        _parse_object(_dict_value(row, "object"))
        for row in _list(raw, "objects")
    )
    claims = tuple(
        _parse_claim(_dict_value(row, "claim"))
        for row in _list(raw, "claims")
    )

    policy_by_id = _unique_by(
        policies, lambda policy: policy.policy_id, "policy_id"
    )
    object_by_id = _unique_by(
        objects, lambda obj: obj.object_id, "object_id"
    )
    claim_by_id = _unique_by(claims, lambda claim: claim.claim_id, "claim_id")

    duplicate_nodes = set(object_by_id) & set(claim_by_id)
    if duplicate_nodes:
        raise ECIRError(
            "object and claim identifiers overlap: "
            + ", ".join(sorted(duplicate_nodes))
        )
    missing_mandatory = set(contract.mandatory_claim_ids) - set(claim_by_id)
    if missing_mandatory:
        raise ECIRError(
            "mandatory claims are not declared: "
            + ", ".join(sorted(missing_mandatory))
        )
    for claim in claims:
        if claim.policy_id not in policy_by_id:
            raise ECIRError(
                f"claim {claim.claim_id} refers to unknown policy {claim.policy_id}"
            )
    for command in commands:
        if command.supports_claim_id not in claim_by_id:
            raise ECIRError(
                f"command {command.command_id} supports unknown claim "
                f"{command.supports_claim_id}"
            )
        missing_dependencies = set(command.dependencies) - (
            set(object_by_id) | set(claim_by_id)
        )
        if missing_dependencies:
            raise ECIRError(
                f"command {command.command_id} has undeclared dependencies: "
                + ", ".join(sorted(missing_dependencies))
            )
        matching_environments = [
            object_by_id[dependency_id]
            for dependency_id in command.dependencies
            if dependency_id in object_by_id
            and object_by_id[dependency_id].kind is ObjectKind.ENVIRONMENT
            and object_by_id[dependency_id].payload_digest
            == command.environment_digest
        ]
        if not matching_environments:
            raise ECIRError(
                f"command {command.command_id} is not bound to a matching "
                "environment object"
            )
        claim = claim_by_id[command.supports_claim_id]
        required_environment = policy_by_id[
            claim.policy_id
        ].required_environment_digest
        if (
            required_environment is not None
            and required_environment != command.environment_digest
        ):
            raise ECIRError(
                f"command {command.command_id} environment does not match "
                f"policy {claim.policy_id}"
            )

    document = ECIRDocument(
        version=version,
        contract=contract,
        policies=policies,
        objects=objects,
        claims=claims,
        commands=commands,
    )
    try:
        document.instantiate_runtime()
    except (ValueError, JITCError) as exc:
        raise ECIRError(f"invalid declaration order or dependency: {exc}") from exc
    return document


def _parse_policy(row: dict[str, Any]) -> AdmissionPolicy:
    _reject_unknown(
        row,
        {
            "policy_id",
            "minimum_passes",
            "allowed_verifier_ids",
            "minimum_distinct_mechanisms",
            "minimum_distinct_implementations",
            "minimum_distinct_data_sources",
            "require_authority_separation",
            "required_environment_digest",
        },
        "policy",
    )
    return AdmissionPolicy(
        policy_id=_text(row, "policy_id"),
        minimum_passes=_integer(row, "minimum_passes", default=1),
        allowed_verifier_ids=_text_tuple(
            row, "allowed_verifier_ids", default=()
        ),
        minimum_distinct_mechanisms=_integer(
            row, "minimum_distinct_mechanisms", default=1
        ),
        minimum_distinct_implementations=_integer(
            row, "minimum_distinct_implementations", default=1
        ),
        minimum_distinct_data_sources=_integer(
            row, "minimum_distinct_data_sources", default=0
        ),
        require_authority_separation=_boolean(
            row, "require_authority_separation", default=True
        ),
        required_environment_digest=_optional_text(
            row, "required_environment_digest"
        ),
    )


def _parse_object(row: dict[str, Any]) -> EpistemicObject:
    _reject_unknown(
        row,
        {
            "object_id",
            "kind",
            "payload_digest",
            "producer_id",
            "dependencies",
            "scope",
        },
        "object",
    )
    try:
        kind = ObjectKind(_text(row, "kind"))
    except ValueError as exc:
        raise ECIRError(f"unknown object kind: {row.get('kind')}") from exc
    return EpistemicObject(
        object_id=_text(row, "object_id"),
        kind=kind,
        payload_digest=_text(row, "payload_digest"),
        producer_id=_text(row, "producer_id"),
        dependencies=_text_tuple(row, "dependencies", default=()),
        scope=_text(row, "scope", default="task"),
    )


def _parse_claim(row: dict[str, Any]) -> ClaimSpec:
    _reject_unknown(
        row,
        {
            "claim_id",
            "statement_digest",
            "proposer_id",
            "policy_id",
            "dependencies",
            "scope",
        },
        "claim",
    )
    return ClaimSpec(
        claim_id=_text(row, "claim_id"),
        statement_digest=_text(row, "statement_digest"),
        proposer_id=_text(row, "proposer_id"),
        policy_id=_text(row, "policy_id"),
        dependencies=_text_tuple(row, "dependencies", default=()),
        scope=_text(row, "scope", default="task"),
    )


def _parse_command(row: dict[str, Any]) -> CommandSpec:
    _reject_unknown(
        row,
        {
            "command_id",
            "action_id",
            "capability_id",
            "argv",
            "cwd",
            "supports_claim_id",
            "dependencies",
            "environment_files",
            "environment_digest",
            "expected_exit_code",
            "timeout_seconds",
            "output_limit_bytes",
        },
        "command",
    )
    return CommandSpec(
        command_id=_text(row, "command_id"),
        action_id=_text(row, "action_id"),
        capability_id=_text(row, "capability_id"),
        argv=_text_tuple(row, "argv"),
        cwd=_text(row, "cwd"),
        supports_claim_id=_text(row, "supports_claim_id"),
        dependencies=_text_tuple(row, "dependencies", default=()),
        environment_files=_text_tuple(row, "environment_files"),
        environment_digest=_text(row, "environment_digest"),
        expected_exit_code=_integer(row, "expected_exit_code", default=0),
        timeout_seconds=_integer(row, "timeout_seconds", default=120),
        output_limit_bytes=_integer(row, "output_limit_bytes", default=32768),
    )


def _unique_by(
    values: tuple[Any, ...],
    key: Callable[[Any], str],
    name: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for value in values:
        item_key = key(value)
        if item_key in result:
            raise ECIRError(f"duplicate {name}: {item_key}")
        result[item_key] = value
    return result


def _reject_unknown(
    row: dict[str, Any], allowed: set[str], context: str
) -> None:
    unknown = set(row) - allowed
    if unknown:
        raise ECIRError(
            f"unknown {context} fields: " + ", ".join(sorted(unknown))
        )


def _dict_value(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ECIRError(f"{context} must be an object")
    return value


def _list(row: dict[str, Any], key: str) -> list[Any]:
    value = row.get(key)
    if not isinstance(value, list):
        raise ECIRError(f"{key} must be an array")
    return value


def _text(row: dict[str, Any], key: str, default: str | None = None) -> str:
    value = row.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise ECIRError(f"{key} must be a non-empty string")
    return value


def _optional_text(row: dict[str, Any], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ECIRError(f"{key} must be null or a non-empty string")
    return value


def _text_tuple(
    row: dict[str, Any], key: str, default: tuple[str, ...] | None = None
) -> tuple[str, ...]:
    value = row.get(key, default)
    if not isinstance(value, (list, tuple)):
        raise ECIRError(f"{key} must be an array of strings")
    if any(not isinstance(item, str) or not item for item in value):
        raise ECIRError(f"{key} must contain only non-empty strings")
    return tuple(value)


def _integer(row: dict[str, Any], key: str, default: int) -> int:
    value = row.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ECIRError(f"{key} must be an integer")
    return value


def _boolean(row: dict[str, Any], key: str, default: bool) -> bool:
    value = row.get(key, default)
    if not isinstance(value, bool):
        raise ECIRError(f"{key} must be a boolean")
    return value
