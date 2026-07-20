from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest

from jitc import (
    AdmissionPolicy,
    ClaimSpec,
    CommandSpec,
    ECIRDocument,
    EpistemicObject,
    ObjectKind,
    Permission,
    PermissionDenied,
    RepositoryCommandExecutor,
    TaskContract,
    compute_repository_environment_digest,
    execute_repository_commands,
)


def make_document(command: CommandSpec) -> ECIRDocument:
    policy = AdmissionPolicy(
        policy_id="policy",
        allowed_verifier_ids=("verifier:exit-code",),
        minimum_distinct_data_sources=1,
        required_environment_digest=command.environment_digest,
    )
    environment = EpistemicObject(
        object_id="environment",
        kind=ObjectKind.ENVIRONMENT,
        payload_digest=command.environment_digest,
        producer_id="test",
    )
    claim = ClaimSpec(
        claim_id="claim",
        statement_digest="sha256:command-exits-zero",
        proposer_id="test:proposer",
        policy_id="policy",
        dependencies=("environment",),
    )
    contract = TaskContract(
        contract_id="contract",
        mandatory_claim_ids=("claim",),
        permissions=(Permission("execute", command.resource_id),),
    )
    return ECIRDocument(
        version="0.1",
        contract=contract,
        policies=(policy,),
        objects=(environment,),
        claims=(claim,),
        commands=(command,),
    )


def command_spec(repository_root: Path) -> CommandSpec:
    environment_file = repository_root / "environment.txt"
    environment_file.write_text("stable\n", encoding="utf-8")
    environment_files = ("environment.txt",)
    return CommandSpec(
        command_id="python-self-check",
        action_id="action",
        capability_id="capability:no-shell",
        argv=(sys.executable, "-c", "print('verified')"),
        cwd=".",
        supports_claim_id="claim",
        dependencies=("environment",),
        environment_files=environment_files,
        environment_digest=compute_repository_environment_digest(
            repository_root, environment_files
        ),
    )


def test_real_command_can_produce_an_admitted_evidence_envelope(tmp_path) -> None:
    command = command_spec(tmp_path)
    document = make_document(command)

    run = execute_repository_commands(
        runtime=document.instantiate_runtime(),
        commands=document.commands,
        repository_root=tmp_path,
        allowed_executables=(sys.executable,),
    )

    assert run.envelope.complete
    assert run.envelope.established_claim_ids == ("claim",)
    assert run.executions[0].return_code == 0
    assert run.executions[0].stdout_preview == "verified\n"
    assert run.runtime.ledger.verify_integrity()


def test_changed_command_cannot_reuse_existing_authorization(tmp_path) -> None:
    original = command_spec(tmp_path)
    document = make_document(original)
    runtime = document.instantiate_runtime()
    token = runtime.authorize_action(original.action_request())
    changed = replace(original, argv=(sys.executable, "-c", "print('changed')"))
    executor = RepositoryCommandExecutor(
        repository_root=tmp_path,
        runtime=runtime,
        allowed_executables=(sys.executable,),
    )

    with pytest.raises(PermissionDenied, match="does not match"):
        executor.execute(changed, token)


def test_host_executable_allowlist_is_an_independent_gate(tmp_path) -> None:
    command = command_spec(tmp_path)
    document = make_document(command)
    runtime = document.instantiate_runtime()
    token = runtime.authorize_action(command.action_request())
    executor = RepositoryCommandExecutor(
        repository_root=tmp_path,
        runtime=runtime,
        allowed_executables=(),
    )

    with pytest.raises(PermissionDenied, match="not enabled"):
        executor.execute(command, token)


def test_command_working_directory_cannot_escape_repository(tmp_path) -> None:
    with pytest.raises(ValueError, match="inside the repository"):
        replace(command_spec(tmp_path), cwd="../outside")


def test_environment_digest_is_order_independent_and_content_sensitive(
    tmp_path,
) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    first = compute_repository_environment_digest(
        tmp_path, ("a.txt", "b.txt")
    )
    reordered = compute_repository_environment_digest(
        tmp_path, ("b.txt", "a.txt")
    )
    (tmp_path / "b.txt").write_text("changed", encoding="utf-8")
    changed = compute_repository_environment_digest(
        tmp_path, ("a.txt", "b.txt")
    )

    assert first == reordered
    assert changed != first


def test_environment_mismatch_blocks_execution_before_effect(tmp_path) -> None:
    command = command_spec(tmp_path)
    document = make_document(command)
    runtime = document.instantiate_runtime()
    token = runtime.authorize_action(command.action_request())
    (tmp_path / "environment.txt").write_text("tampered\n", encoding="utf-8")
    executor = RepositoryCommandExecutor(
        repository_root=tmp_path,
        runtime=runtime,
        allowed_executables=(sys.executable,),
    )

    with pytest.raises(PermissionDenied, match="measured repository"):
        executor.execute(command, token)


def test_environment_mutation_during_command_prevents_admission(tmp_path) -> None:
    original = command_spec(tmp_path)
    command = replace(
        original,
        argv=(
            sys.executable,
            "-c",
            "from pathlib import Path; "
            "Path('environment.txt').write_text('mutated\\n')",
        ),
    )
    document = make_document(command)

    run = execute_repository_commands(
        runtime=document.instantiate_runtime(),
        commands=document.commands,
        repository_root=tmp_path,
        allowed_executables=(sys.executable,),
    )

    assert run.executions[0].return_code == 0
    assert run.executions[0].environment_digest_after != command.environment_digest
    assert not run.envelope.complete
