from __future__ import annotations

import pytest

from jitc.experiment import (
    CapabilityRegistry,
    EvaluationCase,
    ExactMatchAdjudicator,
    ExperimentConfig,
    FunctionProposer,
    ManualCapability,
    TaskInstance,
    evaluate_condition,
    evaluate_intervention,
    run_stage_b_demo,
    stage_b_demo_inputs,
)


def test_intervention_loss_declines_as_registry_covers_families() -> None:
    comparisons = run_stage_b_demo()

    assert [comparison.delta_utility for comparison in comparisons] == pytest.approx(
        [1.0, 2 / 3, 1 / 3]
    )
    assert [
        comparison.original.coverage for comparison in comparisons
    ] == pytest.approx([1.0, 1.0, 1.0])
    assert [
        comparison.intervention.coverage for comparison in comparisons
    ] == pytest.approx([0.0, 1 / 3, 2 / 3])
    assert [
        comparison.original.proposer_calls for comparison in comparisons
    ] == [6, 4, 2]


def test_near_match_guard_rejects_reuse_and_routes_to_proposer() -> None:
    cases, registries, original, intervention = stage_b_demo_inputs()
    near_match = tuple(
        case
        for case in cases
        if case.task.task_id == "normalize-near-match"
    )

    comparison = evaluate_intervention(
        cases=near_match,
        registry=registries[1],
        original_proposer=original,
        intervention_proposer=intervention,
        adjudicator=ExactMatchAdjudicator(),
    )

    original_outcome = comparison.original.outcomes[0]
    intervention_outcome = comparison.intervention.outcomes[0]
    assert original_outcome.valid
    assert original_outcome.route == "proposer"
    assert original_outcome.guard_rejection_ids == (
        "capability:normalize-v1",
    )
    assert not original_outcome.capability_attempted
    assert not intervention_outcome.valid
    assert intervention_outcome.route == "unresolved"


def test_invalid_capability_counts_negative_transfer_then_falls_back() -> None:
    case = EvaluationCase(
        TaskInstance("task", "family", attributes=(("value", "input"),)),
        "correct",
    )
    bad_capability = ManualCapability(
        capability_id="capability:bad",
        family_id="family",
        implementation=lambda task: "wrong",
    )
    registry = CapabilityRegistry("checkpoint:bad", (bad_capability,))
    proposer = FunctionProposer(
        proposer_id="proposer:recovery",
        handlers={"family": lambda task: "correct"},
        call_cost_units=0.5,
    )

    report = evaluate_condition(
        condition_id="bad-reuse",
        cases=(case,),
        registry=registry,
        proposer=proposer,
        adjudicator=ExactMatchAdjudicator(),
    )

    outcome = report.outcomes[0]
    assert outcome.valid
    assert outcome.negative_transfer
    assert outcome.route == "proposer-after-capability-failure"
    assert report.capability_attempts == 1
    assert report.capability_successes == 0
    assert report.reuse_precision == 0.0
    assert report.proposer_calls == 1


def test_all_in_cost_amortizes_capability_lifecycle_cost() -> None:
    case = EvaluationCase(TaskInstance("task", "family"), "answer")
    capability = ManualCapability(
        capability_id="capability",
        family_id="family",
        implementation=lambda task: "answer",
        promotion_cost_units=1.0,
        validation_cost_units=2.0,
        maintenance_cost_units=3.0,
    )
    report = evaluate_condition(
        condition_id="cost",
        cases=(case,),
        registry=CapabilityRegistry("checkpoint", (capability,)),
        proposer=FunctionProposer(
            proposer_id="unused",
            handlers={},
            call_cost_units=1.0,
        ),
        adjudicator=ExactMatchAdjudicator(),
        config=ExperimentConfig(lifecycle_amortization_tasks=10),
    )

    assert report.allocated_lifecycle_cost_units == pytest.approx(0.6)
    assert report.all_in_cost_units == pytest.approx(
        report.online_cost_units + 0.6
    )


def test_all_in_cost_includes_non_model_baseline_lifecycle_cost() -> None:
    case = EvaluationCase(TaskInstance("task", "family"), "answer")
    proposer = FunctionProposer(
        proposer_id="workflow",
        handlers={"family": lambda task: "answer"},
        call_cost_units=0.1,
        lifecycle_cost_units=5.0,
    )

    report = evaluate_condition(
        condition_id="workflow",
        cases=(case,),
        registry=CapabilityRegistry("cold"),
        proposer=proposer,
        adjudicator=ExactMatchAdjudicator(),
        config=ExperimentConfig(lifecycle_amortization_tasks=10),
    )

    assert report.allocated_lifecycle_cost_units == pytest.approx(0.5)


def test_lower_proposer_cost_alone_does_not_hide_intervention_loss() -> None:
    comparison = run_stage_b_demo()[0]

    assert (
        comparison.intervention.proposer_cost_units
        < comparison.original.proposer_cost_units
    )
    assert comparison.intervention.mean_utility == 0.0
    assert comparison.delta_utility == 1.0
