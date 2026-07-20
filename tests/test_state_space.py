from __future__ import annotations

from datetime import datetime, timezone
from itertools import product

from jitc import (
    AdmissionPolicy,
    ClaimSpec,
    EpistemicObject,
    EpistemicRuntime,
    JITCError,
    ObjectKind,
    TaskContract,
    VerificationResult,
)


ACTIONS = (
    "external_pass",
    "self_pass",
    "external_fail",
    "admit",
    "retract",
)


def make_runtime() -> EpistemicRuntime:
    now = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)
    runtime = EpistemicRuntime(
        TaskContract("contract", ("claim",)),
        clock=lambda: now,
    )
    runtime.register_policy(AdmissionPolicy("policy"))
    runtime.declare_object(
        EpistemicObject(
            "observation",
            ObjectKind.OBSERVATION,
            "sha256:observation",
            "tool",
        )
    )
    runtime.propose_claim(
        ClaimSpec(
            "claim",
            "sha256:claim",
            "model",
            "policy",
            ("observation",),
        )
    )
    return runtime


def add_result(
    runtime: EpistemicRuntime,
    *,
    index: int,
    passed: bool,
    authority: str,
) -> None:
    now = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)
    runtime.record_verification(
        VerificationResult(
            result_id=f"result-{index}",
            claim_id="claim",
            passed=passed,
            verifier_id="verifier",
            verifier_version="1",
            authority_id=authority,
            mechanism="execution",
            implementation="test-runner",
            data_sources=("hidden-suite",),
            dependencies=("observation",),
            environment_digest="sha256:environment",
            issued_at=now,
        )
    )


def test_bounded_transition_sequences_preserve_invariants() -> None:
    for sequence in product(ACTIONS, repeat=4):
        runtime = make_runtime()
        external_pass_recorded = False

        for index, action in enumerate(sequence):
            try:
                if action == "external_pass":
                    add_result(
                        runtime,
                        index=index,
                        passed=True,
                        authority="independent",
                    )
                    external_pass_recorded = True
                elif action == "self_pass":
                    add_result(
                        runtime,
                        index=index,
                        passed=True,
                        authority="model",
                    )
                elif action == "external_fail":
                    add_result(
                        runtime,
                        index=index,
                        passed=False,
                        authority="independent",
                    )
                elif action == "admit":
                    runtime.admit_claim("claim")
                elif action == "retract":
                    runtime.retract("observation", "bounded exploration")
            except JITCError:
                pass

            runtime.assert_invariants()
            if runtime.claim_is_established("claim"):
                assert external_pass_recorded
                assert "observation" not in runtime.retracted_ids
