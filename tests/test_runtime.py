from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from jitc import (
    ActionRequest,
    AdmissionDenied,
    AdmissionPolicy,
    CircularSupport,
    ClaimSpec,
    EpistemicObject,
    EpistemicRuntime,
    InvariantViolation,
    ObjectKind,
    Permission,
    PermissionDenied,
    TaskContract,
    VerificationResult,
)


class MutableClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, delta: timedelta) -> None:
        self.value += delta


def make_runtime(
    *,
    policy: AdmissionPolicy | None = None,
    permissions: tuple[Permission, ...] = (),
) -> tuple[EpistemicRuntime, MutableClock]:
    clock = MutableClock()
    contract = TaskContract(
        contract_id="contract-1",
        mandatory_claim_ids=("claim-1",),
        permissions=permissions,
    )
    runtime = EpistemicRuntime(contract, clock=clock)
    runtime.register_policy(policy or AdmissionPolicy(policy_id="policy-1"))
    runtime.declare_object(
        EpistemicObject(
            object_id="observation-1",
            kind=ObjectKind.OBSERVATION,
            payload_digest="sha256:observation",
            producer_id="tool:test-runner",
        )
    )
    runtime.propose_claim(
        ClaimSpec(
            claim_id="claim-1",
            statement_digest="sha256:claim",
            proposer_id="model:proposer",
            policy_id=(policy.policy_id if policy else "policy-1"),
            dependencies=("observation-1",),
        )
    )
    return runtime, clock


def verification(
    clock: MutableClock,
    *,
    result_id: str,
    passed: bool = True,
    authority_id: str = "authority:independent",
    mechanism: str = "test",
    implementation: str = "pytest",
    data_sources: tuple[str, ...] = ("source:hidden-tests",),
    claim_id: str = "claim-1",
    dependencies: tuple[str, ...] = ("observation-1",),
    expires_at: datetime | None = None,
) -> VerificationResult:
    return VerificationResult(
        result_id=result_id,
        claim_id=claim_id,
        passed=passed,
        verifier_id=f"verifier:{implementation}",
        verifier_version="1",
        authority_id=authority_id,
        mechanism=mechanism,
        implementation=implementation,
        data_sources=data_sources,
        dependencies=dependencies,
        environment_digest="sha256:environment",
        issued_at=clock(),
        expires_at=expires_at,
    )


def test_proposer_cannot_self_attest() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(
            clock,
            result_id="verification-self",
            authority_id="model:proposer",
        )
    )

    with pytest.raises(AdmissionDenied, match="needs 1 passing"):
        runtime.admit_claim("claim-1")

    assert not runtime.claim_is_established("claim-1")
    runtime.assert_invariants()


def test_policy_requires_multiple_independence_dimensions() -> None:
    policy = AdmissionPolicy(
        policy_id="policy-independent",
        minimum_passes=2,
        minimum_distinct_mechanisms=2,
        minimum_distinct_implementations=2,
        minimum_distinct_data_sources=2,
    )
    runtime, clock = make_runtime(policy=policy)
    runtime.record_verification(
        verification(
            clock,
            result_id="verification-tests",
            mechanism="execution",
            implementation="pytest",
            data_sources=("source:hidden-tests",),
        )
    )

    with pytest.raises(AdmissionDenied):
        runtime.admit_claim("claim-1")

    runtime.record_verification(
        verification(
            clock,
            result_id="verification-static",
            mechanism="static-analysis",
            implementation="mypy",
            data_sources=("source:type-contracts",),
        )
    )
    decision = runtime.admit_claim("claim-1")

    assert decision.admissible
    assert decision.evidence_ids == (
        "verification-static",
        "verification-tests",
    )
    assert runtime.claim_is_established("claim-1")
    runtime.assert_invariants()


def test_failed_verification_cannot_admit_a_claim() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(clock, result_id="verification-failed", passed=False)
    )

    with pytest.raises(AdmissionDenied):
        runtime.admit_claim("claim-1")

    assert not runtime.emit_envelope().complete


def test_retraction_propagates_over_declared_dependencies() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(clock, result_id="verification-parent")
    )
    runtime.admit_claim("claim-1")
    runtime.propose_claim(
        ClaimSpec(
            claim_id="claim-2",
            statement_digest="sha256:claim-2",
            proposer_id="model:other",
            policy_id="policy-1",
            dependencies=("claim-1",),
        )
    )
    runtime.record_verification(
        verification(
            clock,
            result_id="verification-child",
            claim_id="claim-2",
            dependencies=("claim-1",),
        )
    )
    runtime.admit_claim("claim-2")

    report = runtime.retract("observation-1", "source was withdrawn")

    assert set(report.retracted_ids) == {
        "observation-1",
        "claim-1",
        "claim-2",
    }
    assert not runtime.claim_is_established("claim-1")
    assert not runtime.claim_is_established("claim-2")
    assert not runtime.emit_envelope().complete
    runtime.assert_invariants()


def test_expired_evidence_loses_current_admissibility() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(
            clock,
            result_id="verification-expiring",
            expires_at=clock() + timedelta(minutes=5),
        )
    )
    runtime.admit_claim("claim-1")
    assert runtime.emit_envelope().complete

    clock.advance(timedelta(minutes=6))

    assert not runtime.claim_is_established("claim-1")
    envelope = runtime.emit_envelope()
    assert not envelope.complete
    assert envelope.unresolved_claim_ids == ("claim-1",)
    runtime.assert_invariants()


def test_revoking_verification_invalidates_claim_without_erasing_history() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(clock, result_id="verification-revoked")
    )
    runtime.admit_claim("claim-1")

    report = runtime.retract(
        "verification-revoked", "verifier implementation was compromised"
    )

    assert report.retracted_ids == ()
    assert report.invalidated_claim_ids == ("claim-1",)
    assert not runtime.claim_is_established("claim-1")
    assert runtime.ledger.verify_integrity()


def test_permissions_are_exact_not_prefix_based() -> None:
    permission = Permission(effect="read", resource="repo://shop/src")
    runtime, _ = make_runtime(permissions=(permission,))

    token = runtime.authorize_action(
        ActionRequest(
            action_id="action-allowed",
            capability_id="capability:reader",
            effect="read",
            resource="repo://shop/src",
        )
    )
    assert token.effect == "read"

    with pytest.raises(PermissionDenied):
        runtime.authorize_action(
            ActionRequest(
                action_id="action-denied",
                capability_id="capability:reader",
                effect="read",
                resource="repo://shop/src/secrets",
            )
        )

    runtime.assert_invariants()


def test_verification_cannot_depend_on_a_downstream_claim() -> None:
    runtime, clock = make_runtime()
    runtime.propose_claim(
        ClaimSpec(
            claim_id="claim-child",
            statement_digest="sha256:child",
            proposer_id="model:child",
            policy_id="policy-1",
            dependencies=("claim-1",),
        )
    )

    with pytest.raises(CircularSupport):
        runtime.record_verification(
            verification(
                clock,
                result_id="verification-circular",
                dependencies=("claim-child",),
            )
        )


def test_complete_envelope_names_evidence_and_ledger_head() -> None:
    runtime, clock = make_runtime()
    runtime.record_verification(
        verification(clock, result_id="verification-envelope")
    )
    runtime.admit_claim("claim-1")

    envelope = runtime.emit_envelope()

    assert envelope.complete
    assert envelope.established_claim_ids == ("claim-1",)
    assert envelope.evidence_ids == ("verification-envelope",)
    assert envelope.ledger_head_hash == runtime.ledger.head_hash
    runtime.assert_invariants()


def test_ledger_detects_historical_mutation() -> None:
    runtime, _ = make_runtime()
    first = runtime.ledger._events[0]
    runtime.ledger._events[0] = replace(first, subject_id="tampered")

    assert not runtime.ledger.verify_integrity()
    with pytest.raises(InvariantViolation):
        runtime.assert_invariants()
