from __future__ import annotations

from dataclasses import replace

import pytest

from jitc.experiment import CapabilityRegistry, evaluate_intervention
from jitc.repository_pilot import (
    PatchSet,
    build_repository_pilot,
    run_repository_pilot,
)


def test_repository_pilot_intervention_loss_declines() -> None:
    report = run_repository_pilot()

    assert report.benchmark_definition_digest == (
        "sha256:bf951d6083a987fc4f8e4ce311ed2c626d84ec5303f2d4816320476926499060"
    )
    assert [
        comparison.delta_utility
        for comparison in report.intervention_curve
    ] == pytest.approx([1.0, 2 / 3, 1 / 3])
    assert [
        comparison.original.coverage
        for comparison in report.intervention_curve
    ] == pytest.approx([1.0, 1.0, 1.0])
    assert [
        comparison.intervention.coverage
        for comparison in report.intervention_curve
    ] == pytest.approx([0.0, 1 / 3, 2 / 3])


def test_shifted_near_match_rejects_capability_and_uses_proposer() -> None:
    inputs = build_repository_pilot()
    shifted = tuple(
        case
        for case in inputs.cases
        if case.task.task_id == "repo:config-shifted-near-match"
    )

    comparison = evaluate_intervention(
        cases=shifted,
        registry=inputs.registries[1],
        original_proposer=inputs.original_proposer,
        intervention_proposer=inputs.null_proposer,
        adjudicator=inputs.adjudicator,
        config=inputs.config,
    )

    original = comparison.original.outcomes[0]
    assert original.valid
    assert original.route == "proposer"
    assert original.guard_rejection_ids == (
        "capability:repository-config-v1",
    )
    assert not comparison.intervention.outcomes[0].valid


def test_overbroad_guard_creates_visible_negative_transfer() -> None:
    inputs = build_repository_pilot()
    shifted = tuple(
        case
        for case in inputs.cases
        if case.task.task_id == "repo:config-shifted-near-match"
    )
    original_capability = inputs.registries[1].capabilities[0]
    overbroad = replace(original_capability, required_environment=())

    comparison = evaluate_intervention(
        cases=shifted,
        registry=CapabilityRegistry("overbroad", (overbroad,)),
        original_proposer=inputs.original_proposer,
        intervention_proposer=inputs.null_proposer,
        adjudicator=inputs.adjudicator,
        config=inputs.config,
    )

    recovered = comparison.original.outcomes[0]
    assert recovered.valid
    assert recovered.negative_transfer
    assert recovered.route == "proposer-after-capability-failure"
    assert recovered.failure_reason == "capability output rejected by adjudicator"


def test_patch_path_escape_is_rejected_by_parser_and_adjudicator() -> None:
    inputs = build_repository_pilot()
    case = inputs.cases[0]
    candidate = '{"changes":[{"content":"escape","path":"../escape"}]}'

    with pytest.raises(ValueError, match="canonical relative"):
        PatchSet.from_json(candidate)
    adjudication = inputs.adjudicator.adjudicate(case, candidate)
    assert not adjudication.valid


def test_classical_baselines_are_reported_on_identical_cases() -> None:
    report = run_repository_pilot()
    baselines = {
        baseline.condition_id: baseline for baseline in report.baselines
    }

    assert baselines["baseline:direct-strong"].coverage == 1.0
    assert baselines["baseline:deterministic-workflow"].coverage == pytest.approx(
        5 / 6
    )
    assert baselines["baseline:snapshot-retrieval"].coverage == pytest.approx(
        2 / 6
    )
    assert baselines["baseline:null"].coverage == 0.0
    task_sequences = {
        tuple(outcome.task_id for outcome in baseline.outcomes)
        for baseline in baselines.values()
    }
    assert len(task_sequences) == 1
