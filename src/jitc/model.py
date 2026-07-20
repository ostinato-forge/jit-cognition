from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_text(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _require_unique(name: str, values: tuple[str, ...]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not contain duplicates")


def _require_aware(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


class ObjectKind(str, Enum):
    OBSERVATION = "observation"
    ASSUMPTION = "assumption"
    ARTIFACT = "artifact"
    CAPABILITY = "capability"
    ENVIRONMENT = "environment"
    SOURCE = "source"
    VERIFIER = "verifier"


@dataclass(frozen=True, slots=True)
class EpistemicObject:
    object_id: str
    kind: ObjectKind
    payload_digest: str
    producer_id: str
    dependencies: tuple[str, ...] = ()
    scope: str = "task"

    def __post_init__(self) -> None:
        _require_text("object_id", self.object_id)
        _require_text("payload_digest", self.payload_digest)
        _require_text("producer_id", self.producer_id)
        _require_text("scope", self.scope)
        _require_unique("dependencies", self.dependencies)
        if self.object_id in self.dependencies:
            raise ValueError("an object cannot depend on itself")


@dataclass(frozen=True, slots=True)
class ClaimSpec:
    claim_id: str
    statement_digest: str
    proposer_id: str
    policy_id: str
    dependencies: tuple[str, ...] = ()
    scope: str = "task"

    def __post_init__(self) -> None:
        _require_text("claim_id", self.claim_id)
        _require_text("statement_digest", self.statement_digest)
        _require_text("proposer_id", self.proposer_id)
        _require_text("policy_id", self.policy_id)
        _require_text("scope", self.scope)
        _require_unique("dependencies", self.dependencies)
        if self.claim_id in self.dependencies:
            raise ValueError("a claim cannot depend on itself")


@dataclass(frozen=True, slots=True)
class AdmissionPolicy:
    policy_id: str
    minimum_passes: int = 1
    allowed_verifier_ids: tuple[str, ...] = ()
    minimum_distinct_mechanisms: int = 1
    minimum_distinct_implementations: int = 1
    minimum_distinct_data_sources: int = 0
    require_authority_separation: bool = True
    required_environment_digest: str | None = None

    def __post_init__(self) -> None:
        _require_text("policy_id", self.policy_id)
        _require_unique("allowed_verifier_ids", self.allowed_verifier_ids)
        if self.minimum_passes < 1:
            raise ValueError("minimum_passes must be at least one")
        for name, value in (
            ("minimum_distinct_mechanisms", self.minimum_distinct_mechanisms),
            (
                "minimum_distinct_implementations",
                self.minimum_distinct_implementations,
            ),
            ("minimum_distinct_data_sources", self.minimum_distinct_data_sources),
        ):
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.required_environment_digest is not None:
            _require_text(
                "required_environment_digest", self.required_environment_digest
            )


@dataclass(frozen=True, slots=True)
class VerificationResult:
    result_id: str
    claim_id: str
    passed: bool
    verifier_id: str
    verifier_version: str
    authority_id: str
    mechanism: str
    implementation: str
    data_sources: tuple[str, ...]
    dependencies: tuple[str, ...]
    environment_digest: str
    issued_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("result_id", self.result_id),
            ("claim_id", self.claim_id),
            ("verifier_id", self.verifier_id),
            ("verifier_version", self.verifier_version),
            ("authority_id", self.authority_id),
            ("mechanism", self.mechanism),
            ("implementation", self.implementation),
            ("environment_digest", self.environment_digest),
        ):
            _require_text(name, value)
        _require_unique("data_sources", self.data_sources)
        _require_unique("dependencies", self.dependencies)
        _require_aware("issued_at", self.issued_at)
        if self.expires_at is not None:
            _require_aware("expires_at", self.expires_at)
            if self.expires_at <= self.issued_at:
                raise ValueError("expires_at must be later than issued_at")


@dataclass(frozen=True, slots=True)
class Permission:
    effect: str
    resource: str

    def __post_init__(self) -> None:
        _require_text("effect", self.effect)
        _require_text("resource", self.resource)


@dataclass(frozen=True, slots=True)
class TaskContract:
    contract_id: str
    mandatory_claim_ids: tuple[str, ...]
    permissions: tuple[Permission, ...] = ()

    def __post_init__(self) -> None:
        _require_text("contract_id", self.contract_id)
        _require_unique("mandatory_claim_ids", self.mandatory_claim_ids)
        if len(self.permissions) != len(set(self.permissions)):
            raise ValueError("permissions must not contain duplicates")


@dataclass(frozen=True, slots=True)
class ActionRequest:
    action_id: str
    capability_id: str
    effect: str
    resource: str

    def __post_init__(self) -> None:
        for name, value in (
            ("action_id", self.action_id),
            ("capability_id", self.capability_id),
            ("effect", self.effect),
            ("resource", self.resource),
        ):
            _require_text(name, value)


@dataclass(frozen=True, slots=True)
class AuthorizationToken:
    action_id: str
    contract_id: str
    effect: str
    resource: str
    authorization_event_hash: str


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    admissible: bool
    evidence_ids: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetractionReport:
    root_id: str
    retracted_ids: tuple[str, ...]
    invalidated_claim_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ArtifactEnvelope:
    contract_id: str
    complete: bool
    established_claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    unresolved_claim_ids: tuple[str, ...]
    ledger_head_hash: str
