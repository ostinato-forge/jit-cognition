from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from typing import Callable, Mapping, Protocol, Sequence


TaskHandler = Callable[["TaskInstance"], str]


def _require_text(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _require_nonnegative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _require_key_values(
    name: str, values: tuple[tuple[str, str], ...]
) -> None:
    keys = tuple(key for key, _ in values)
    if len(keys) != len(set(keys)):
        raise ValueError(f"{name} keys must be unique")
    for key, value in values:
        _require_text(f"{name} key", key)
        _require_text(f"{name} value", value)


@dataclass(frozen=True, slots=True)
class TaskInstance:
    """Proposer-visible task data.

    Expected outputs deliberately live in EvaluationCase, not here, so a
    proposer or capability does not receive the hidden adjudication target.
    """

    task_id: str
    family_id: str
    attributes: tuple[tuple[str, str], ...] = ()
    environment: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_text("task_id", self.task_id)
        _require_text("family_id", self.family_id)
        _require_key_values("attributes", self.attributes)
        _require_key_values("environment", self.environment)

    def attribute(self, key: str) -> str | None:
        return dict(self.attributes).get(key)

    def environment_value(self, key: str) -> str | None:
        return dict(self.environment).get(key)


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    task: TaskInstance
    expected_output: str


@dataclass(frozen=True, slots=True)
class GuardDecision:
    applicable: bool
    failures: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ManualCapability:
    capability_id: str
    family_id: str
    implementation: TaskHandler = field(repr=False, compare=False)
    required_attributes: tuple[tuple[str, str], ...] = ()
    required_environment: tuple[tuple[str, str], ...] = ()
    execution_cost_units: float = 0.1
    promotion_cost_units: float = 0.0
    validation_cost_units: float = 0.0
    maintenance_cost_units: float = 0.0

    def __post_init__(self) -> None:
        _require_text("capability_id", self.capability_id)
        _require_text("family_id", self.family_id)
        _require_key_values("required_attributes", self.required_attributes)
        _require_key_values("required_environment", self.required_environment)
        for name, value in (
            ("execution_cost_units", self.execution_cost_units),
            ("promotion_cost_units", self.promotion_cost_units),
            ("validation_cost_units", self.validation_cost_units),
            ("maintenance_cost_units", self.maintenance_cost_units),
        ):
            _require_nonnegative(name, value)

    @property
    def lifecycle_cost_units(self) -> float:
        return (
            self.promotion_cost_units
            + self.validation_cost_units
            + self.maintenance_cost_units
        )

    def guard(self, task: TaskInstance) -> GuardDecision:
        failures: list[str] = []
        if task.family_id != self.family_id:
            failures.append("family mismatch")
        for key, expected in self.required_attributes:
            if task.attribute(key) != expected:
                failures.append(f"attribute mismatch: {key}")
        for key, expected in self.required_environment:
            if task.environment_value(key) != expected:
                failures.append(f"environment mismatch: {key}")
        return GuardDecision(not failures, tuple(failures))

    def execute(self, task: TaskInstance) -> str:
        return self.implementation(task)


@dataclass(frozen=True, slots=True)
class RegistrySelection:
    selected: ManualCapability | None
    rejected_capability_ids: tuple[str, ...]
    ambiguous_capability_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CapabilityRegistry:
    checkpoint_id: str
    capabilities: tuple[ManualCapability, ...] = ()

    def __post_init__(self) -> None:
        _require_text("checkpoint_id", self.checkpoint_id)
        capability_ids = tuple(
            capability.capability_id for capability in self.capabilities
        )
        if len(capability_ids) != len(set(capability_ids)):
            raise ValueError("capability identifiers must be unique")

    @property
    def lifecycle_cost_units(self) -> float:
        return sum(
            capability.lifecycle_cost_units
            for capability in self.capabilities
        )

    def select(self, task: TaskInstance) -> RegistrySelection:
        relevant = tuple(
            capability
            for capability in self.capabilities
            if capability.family_id == task.family_id
        )
        decisions = tuple(
            (capability, capability.guard(task)) for capability in relevant
        )
        applicable = tuple(
            capability
            for capability, decision in decisions
            if decision.applicable
        )
        rejected = tuple(
            capability.capability_id
            for capability, decision in decisions
            if not decision.applicable
        )
        if len(applicable) == 1:
            return RegistrySelection(applicable[0], rejected, ())
        if len(applicable) > 1:
            return RegistrySelection(
                None,
                rejected,
                tuple(
                    capability.capability_id for capability in applicable
                ),
            )
        return RegistrySelection(None, rejected, ())


class Proposer(Protocol):
    proposer_id: str
    call_cost_units: float
    lifecycle_cost_units: float

    def propose(self, task: TaskInstance) -> str | None: ...


class FunctionProposer:
    def __init__(
        self,
        *,
        proposer_id: str,
        handlers: Mapping[str, TaskHandler],
        call_cost_units: float,
        lifecycle_cost_units: float = 0.0,
    ) -> None:
        _require_text("proposer_id", proposer_id)
        _require_nonnegative("call_cost_units", call_cost_units)
        _require_nonnegative("lifecycle_cost_units", lifecycle_cost_units)
        self.proposer_id = proposer_id
        self.call_cost_units = call_cost_units
        self.lifecycle_cost_units = lifecycle_cost_units
        self._handlers = dict(handlers)

    def propose(self, task: TaskInstance) -> str | None:
        handler = self._handlers.get(task.family_id)
        return None if handler is None else handler(task)


class NullProposer:
    def __init__(
        self,
        *,
        proposer_id: str = "proposer:null",
        call_cost_units: float = 0.0,
        lifecycle_cost_units: float = 0.0,
    ) -> None:
        _require_text("proposer_id", proposer_id)
        _require_nonnegative("call_cost_units", call_cost_units)
        _require_nonnegative("lifecycle_cost_units", lifecycle_cost_units)
        self.proposer_id = proposer_id
        self.call_cost_units = call_cost_units
        self.lifecycle_cost_units = lifecycle_cost_units

    def propose(self, task: TaskInstance) -> str | None:
        del task
        return None


@dataclass(frozen=True, slots=True)
class Adjudication:
    valid: bool
    utility: float


class Adjudicator(Protocol):
    def adjudicate(
        self, case: EvaluationCase, candidate: str
    ) -> Adjudication: ...


class ExactMatchAdjudicator:
    """Oracle adjudicator for upper-bound experiments, not a production verifier."""

    def adjudicate(
        self, case: EvaluationCase, candidate: str
    ) -> Adjudication:
        valid = candidate == case.expected_output
        return Adjudication(valid=valid, utility=1.0 if valid else 0.0)


@dataclass(frozen=True, slots=True)
class CostBreakdown:
    lookup_units: float = 0.0
    capability_units: float = 0.0
    proposer_units: float = 0.0
    verification_units: float = 0.0

    @property
    def total_units(self) -> float:
        return (
            self.lookup_units
            + self.capability_units
            + self.proposer_units
            + self.verification_units
        )


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    max_online_cost_per_task: float = 2.0
    lookup_cost_units: float = 0.02
    verification_cost_units: float = 0.05
    lifecycle_amortization_tasks: int = 100

    def __post_init__(self) -> None:
        _require_nonnegative(
            "max_online_cost_per_task", self.max_online_cost_per_task
        )
        _require_nonnegative("lookup_cost_units", self.lookup_cost_units)
        _require_nonnegative(
            "verification_cost_units", self.verification_cost_units
        )
        if self.lifecycle_amortization_tasks < 1:
            raise ValueError("lifecycle_amortization_tasks must be positive")


@dataclass(frozen=True, slots=True)
class TaskOutcome:
    task_id: str
    family_id: str
    route: str
    candidate: str | None
    valid: bool
    utility: float
    capability_id: str | None
    proposer_id: str
    proposer_called: bool
    capability_attempted: bool
    guard_rejection_ids: tuple[str, ...]
    ambiguity_ids: tuple[str, ...]
    negative_transfer: bool
    budget_exhausted: bool
    failure_reason: str | None
    cost: CostBreakdown


@dataclass(frozen=True, slots=True)
class ConditionReport:
    condition_id: str
    checkpoint_id: str
    proposer_id: str
    outcomes: tuple[TaskOutcome, ...]
    allocated_lifecycle_cost_units: float

    @property
    def task_count(self) -> int:
        return len(self.outcomes)

    @property
    def valid_tasks(self) -> int:
        return sum(outcome.valid for outcome in self.outcomes)

    @property
    def mean_utility(self) -> float:
        if not self.outcomes:
            return 0.0
        return sum(outcome.utility for outcome in self.outcomes) / len(
            self.outcomes
        )

    @property
    def coverage(self) -> float:
        if not self.outcomes:
            return 0.0
        return self.valid_tasks / len(self.outcomes)

    @property
    def proposer_calls(self) -> int:
        return sum(outcome.proposer_called for outcome in self.outcomes)

    @property
    def capability_attempts(self) -> int:
        return sum(outcome.capability_attempted for outcome in self.outcomes)

    @property
    def capability_successes(self) -> int:
        return sum(
            outcome.route == "capability" and outcome.valid
            for outcome in self.outcomes
        )

    @property
    def negative_transfers(self) -> int:
        return sum(outcome.negative_transfer for outcome in self.outcomes)

    @property
    def budget_exhaustions(self) -> int:
        return sum(outcome.budget_exhausted for outcome in self.outcomes)

    @property
    def guard_rejections(self) -> int:
        return sum(
            len(outcome.guard_rejection_ids) for outcome in self.outcomes
        )

    @property
    def ambiguous_tasks(self) -> int:
        return sum(bool(outcome.ambiguity_ids) for outcome in self.outcomes)

    @property
    def reuse_precision(self) -> float | None:
        if self.capability_attempts == 0:
            return None
        return self.capability_successes / self.capability_attempts

    @property
    def online_cost_units(self) -> float:
        return sum(outcome.cost.total_units for outcome in self.outcomes)

    @property
    def proposer_cost_units(self) -> float:
        return sum(outcome.cost.proposer_units for outcome in self.outcomes)

    @property
    def all_in_cost_units(self) -> float:
        return self.online_cost_units + self.allocated_lifecycle_cost_units

    def summary(self) -> dict[str, object]:
        return {
            "all_in_cost_units": self.all_in_cost_units,
            "allocated_lifecycle_cost_units": (
                self.allocated_lifecycle_cost_units
            ),
            "ambiguous_tasks": self.ambiguous_tasks,
            "budget_exhaustions": self.budget_exhaustions,
            "capability_attempts": self.capability_attempts,
            "capability_successes": self.capability_successes,
            "coverage": self.coverage,
            "guard_rejections": self.guard_rejections,
            "mean_utility": self.mean_utility,
            "negative_transfers": self.negative_transfers,
            "online_cost_units": self.online_cost_units,
            "proposer_calls": self.proposer_calls,
            "proposer_cost_units": self.proposer_cost_units,
            "reuse_precision": self.reuse_precision,
            "task_count": self.task_count,
            "valid_tasks": self.valid_tasks,
        }

    def to_dict(self, *, include_outcomes: bool = False) -> dict[str, object]:
        result: dict[str, object] = {
            "checkpoint_id": self.checkpoint_id,
            "condition_id": self.condition_id,
            "metrics": self.summary(),
            "proposer_id": self.proposer_id,
        }
        if include_outcomes:
            result["outcomes"] = [
                asdict(outcome) for outcome in self.outcomes
            ]
        return result


@dataclass(frozen=True, slots=True)
class InterventionComparison:
    checkpoint_id: str
    original: ConditionReport
    intervention: ConditionReport
    delta_utility: float
    delta_coverage: float

    @property
    def paired_utility_differences(self) -> tuple[float, ...]:
        return tuple(
            original.utility - intervention.utility
            for original, intervention in zip(
                self.original.outcomes,
                self.intervention.outcomes,
                strict=True,
            )
        )

    def to_dict(self, *, include_outcomes: bool = False) -> dict[str, object]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "delta_coverage": self.delta_coverage,
            "delta_utility": self.delta_utility,
            "intervention": self.intervention.to_dict(
                include_outcomes=include_outcomes
            ),
            "original": self.original.to_dict(
                include_outcomes=include_outcomes
            ),
            "paired_utility_differences": (
                self.paired_utility_differences
            ),
        }


def _evaluate_task(
    *,
    case: EvaluationCase,
    registry: CapabilityRegistry,
    proposer: Proposer,
    adjudicator: Adjudicator,
    config: ExperimentConfig,
) -> TaskOutcome:
    lookup_units = config.lookup_cost_units
    capability_units = 0.0
    proposer_units = 0.0
    verification_units = 0.0
    capability_attempted = False
    capability_id: str | None = None
    negative_transfer = False
    proposer_called = False
    failure_reason: str | None = None
    selection = registry.select(case.task)

    def spent() -> float:
        return (
            lookup_units
            + capability_units
            + proposer_units
            + verification_units
        )

    def finish(
        *,
        route: str,
        candidate: str | None = None,
        valid: bool = False,
        utility: float = 0.0,
        budget_exhausted: bool = False,
    ) -> TaskOutcome:
        return TaskOutcome(
            task_id=case.task.task_id,
            family_id=case.task.family_id,
            route=route,
            candidate=candidate,
            valid=valid,
            utility=utility,
            capability_id=capability_id,
            proposer_id=proposer.proposer_id,
            proposer_called=proposer_called,
            capability_attempted=capability_attempted,
            guard_rejection_ids=selection.rejected_capability_ids,
            ambiguity_ids=selection.ambiguous_capability_ids,
            negative_transfer=negative_transfer,
            budget_exhausted=budget_exhausted,
            failure_reason=failure_reason,
            cost=CostBreakdown(
                lookup_units=lookup_units,
                capability_units=capability_units,
                proposer_units=proposer_units,
                verification_units=verification_units,
            ),
        )

    if spent() > config.max_online_cost_per_task:
        failure_reason = "lookup exceeded online budget"
        return finish(route="budget-exhausted", budget_exhausted=True)

    if selection.selected is not None:
        capability = selection.selected
        if (
            spent() + capability.execution_cost_units
            > config.max_online_cost_per_task
        ):
            failure_reason = "capability execution exceeded online budget"
            return finish(route="budget-exhausted", budget_exhausted=True)
        capability_attempted = True
        capability_id = capability.capability_id
        capability_units += capability.execution_cost_units
        try:
            candidate = capability.execute(case.task)
        except Exception as exc:
            negative_transfer = True
            failure_reason = f"capability raised {type(exc).__name__}"
        else:
            if (
                spent() + config.verification_cost_units
                > config.max_online_cost_per_task
            ):
                failure_reason = "capability verification exceeded online budget"
                return finish(
                    route="budget-exhausted",
                    candidate=candidate,
                    budget_exhausted=True,
                )
            verification_units += config.verification_cost_units
            adjudication = adjudicator.adjudicate(case, candidate)
            if adjudication.valid:
                return finish(
                    route="capability",
                    candidate=candidate,
                    valid=True,
                    utility=adjudication.utility,
                )
            negative_transfer = True
            failure_reason = "capability output rejected by adjudicator"

    if (
        spent() + proposer.call_cost_units
        > config.max_online_cost_per_task
    ):
        failure_reason = "proposer call exceeded online budget"
        return finish(route="budget-exhausted", budget_exhausted=True)
    proposer_called = True
    proposer_units += proposer.call_cost_units
    proposed = proposer.propose(case.task)
    if proposed is None:
        if failure_reason is None:
            failure_reason = "proposer returned unresolved"
        route = (
            "unresolved-after-capability-failure"
            if capability_attempted
            else "unresolved"
        )
        return finish(route=route)
    if (
        spent() + config.verification_cost_units
        > config.max_online_cost_per_task
    ):
        failure_reason = "proposer verification exceeded online budget"
        return finish(
            route="budget-exhausted",
            candidate=proposed,
            budget_exhausted=True,
        )
    verification_units += config.verification_cost_units
    adjudication = adjudicator.adjudicate(case, proposed)
    if capability_attempted:
        route = "proposer-after-capability-failure"
    elif selection.ambiguous_capability_ids:
        route = "proposer-after-ambiguity"
    else:
        route = "proposer"
    if not adjudication.valid:
        failure_reason = "proposer output rejected by adjudicator"
    return finish(
        route=route,
        candidate=proposed,
        valid=adjudication.valid,
        utility=adjudication.utility,
    )


def evaluate_condition(
    *,
    condition_id: str,
    cases: Sequence[EvaluationCase],
    registry: CapabilityRegistry,
    proposer: Proposer,
    adjudicator: Adjudicator,
    config: ExperimentConfig = ExperimentConfig(),
) -> ConditionReport:
    _require_text("condition_id", condition_id)
    case_tuple = tuple(cases)
    task_ids = tuple(case.task.task_id for case in case_tuple)
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("evaluation task identifiers must be unique")
    outcomes = tuple(
        _evaluate_task(
            case=case,
            registry=registry,
            proposer=proposer,
            adjudicator=adjudicator,
            config=config,
        )
        for case in case_tuple
    )
    allocated_lifecycle_cost = (
        (registry.lifecycle_cost_units + proposer.lifecycle_cost_units)
        * len(case_tuple)
        / config.lifecycle_amortization_tasks
    )
    return ConditionReport(
        condition_id=condition_id,
        checkpoint_id=registry.checkpoint_id,
        proposer_id=proposer.proposer_id,
        outcomes=outcomes,
        allocated_lifecycle_cost_units=allocated_lifecycle_cost,
    )


def evaluate_intervention(
    *,
    cases: Sequence[EvaluationCase],
    registry: CapabilityRegistry,
    original_proposer: Proposer,
    intervention_proposer: Proposer,
    adjudicator: Adjudicator,
    config: ExperimentConfig = ExperimentConfig(),
) -> InterventionComparison:
    case_tuple = tuple(cases)
    original = evaluate_condition(
        condition_id="original",
        cases=case_tuple,
        registry=registry,
        proposer=original_proposer,
        adjudicator=adjudicator,
        config=config,
    )
    intervention = evaluate_condition(
        condition_id="intervention",
        cases=case_tuple,
        registry=registry,
        proposer=intervention_proposer,
        adjudicator=adjudicator,
        config=config,
    )
    original_ids = tuple(outcome.task_id for outcome in original.outcomes)
    intervention_ids = tuple(
        outcome.task_id for outcome in intervention.outcomes
    )
    if original_ids != intervention_ids:
        raise RuntimeError("paired conditions evaluated different tasks")
    return InterventionComparison(
        checkpoint_id=registry.checkpoint_id,
        original=original,
        intervention=intervention,
        delta_utility=original.mean_utility - intervention.mean_utility,
        delta_coverage=original.coverage - intervention.coverage,
    )


def evaluate_intervention_curve(
    *,
    cases: Sequence[EvaluationCase],
    registries: Sequence[CapabilityRegistry],
    original_proposer: Proposer,
    intervention_proposer: Proposer,
    adjudicator: Adjudicator,
    config: ExperimentConfig = ExperimentConfig(),
) -> tuple[InterventionComparison, ...]:
    return tuple(
        evaluate_intervention(
            cases=cases,
            registry=registry,
            original_proposer=original_proposer,
            intervention_proposer=intervention_proposer,
            adjudicator=adjudicator,
            config=config,
        )
        for registry in registries
    )


def _required_attribute(task: TaskInstance, key: str) -> str:
    value = task.attribute(key)
    if value is None:
        raise ValueError(f"task lacks required attribute: {key}")
    return value


def _normalize_v1(task: TaskInstance) -> str:
    return (
        _required_attribute(task, "raw")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _normalize_general(task: TaskInstance) -> str:
    if task.environment_value("schema") == "v2":
        return (
            _required_attribute(task, "raw")
            .strip()
            .lower()
            .replace("-", ".")
            .replace(" ", ".")
        )
    return _normalize_v1(task)


def _bump_integer(task: TaskInstance) -> str:
    return str(int(_required_attribute(task, "version")) + 1)


def _redact(task: TaskInstance) -> str:
    _required_attribute(task, "raw")
    return "***"


def stage_b_demo_inputs() -> tuple[
    tuple[EvaluationCase, ...],
    tuple[CapabilityRegistry, ...],
    FunctionProposer,
    NullProposer,
]:
    cases = (
        EvaluationCase(
            TaskInstance(
                "normalize-spaces",
                "normalize-key",
                attributes=(("raw", " Feature Flag "),),
                environment=(("schema", "v1"),),
            ),
            "feature_flag",
        ),
        EvaluationCase(
            TaskInstance(
                "normalize-hyphen",
                "normalize-key",
                attributes=(("raw", "cache-TTL"),),
                environment=(("schema", "v1"),),
            ),
            "cache_ttl",
        ),
        EvaluationCase(
            TaskInstance(
                "normalize-near-match",
                "normalize-key",
                attributes=(("raw", "Feature Flag"),),
                environment=(("schema", "v2"),),
            ),
            "feature.flag",
        ),
        EvaluationCase(
            TaskInstance(
                "bump-three",
                "bump-version",
                attributes=(("version", "3"),),
                environment=(("mode", "integer"),),
            ),
            "4",
        ),
        EvaluationCase(
            TaskInstance(
                "bump-nine",
                "bump-version",
                attributes=(("version", "9"),),
                environment=(("mode", "integer"),),
            ),
            "10",
        ),
        EvaluationCase(
            TaskInstance(
                "novel-redaction",
                "redact-secret",
                attributes=(("raw", "token-value"),),
            ),
            "***",
        ),
    )
    normalize_capability = ManualCapability(
        capability_id="capability:normalize-v1",
        family_id="normalize-key",
        implementation=_normalize_v1,
        required_environment=(("schema", "v1"),),
        promotion_cost_units=2.0,
        validation_cost_units=3.0,
        maintenance_cost_units=0.5,
    )
    bump_capability = ManualCapability(
        capability_id="capability:bump-integer",
        family_id="bump-version",
        implementation=_bump_integer,
        required_environment=(("mode", "integer"),),
        promotion_cost_units=2.5,
        validation_cost_units=3.5,
        maintenance_cost_units=0.5,
    )
    registries = (
        CapabilityRegistry("checkpoint:0-cold"),
        CapabilityRegistry(
            "checkpoint:1-normalize", (normalize_capability,)
        ),
        CapabilityRegistry(
            "checkpoint:2-two-families",
            (normalize_capability, bump_capability),
        ),
    )
    original = FunctionProposer(
        proposer_id="proposer:original-strong",
        handlers={
            "normalize-key": _normalize_general,
            "bump-version": _bump_integer,
            "redact-secret": _redact,
        },
        call_cost_units=1.0,
    )
    intervention = NullProposer(
        proposer_id="proposer:null-intervention",
        call_cost_units=0.05,
    )
    return cases, registries, original, intervention


def run_stage_b_demo() -> tuple[InterventionComparison, ...]:
    cases, registries, original, intervention = stage_b_demo_inputs()
    return evaluate_intervention_curve(
        cases=cases,
        registries=registries,
        original_proposer=original,
        intervention_proposer=intervention,
        adjudicator=ExactMatchAdjudicator(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the constructed JITC Stage B intervention demo"
    )
    parser.add_argument(
        "--include-outcomes",
        action="store_true",
        help="Include every task-level outcome in addition to summaries",
    )
    args = parser.parse_args(argv)
    comparisons = run_stage_b_demo()
    output = {
        "claim_boundary": (
            "Constructed manual-guard upper bound; not evidence that automatic "
            "promotion or real repository transfer works."
        ),
        "comparisons": [
            comparison.to_dict(include_outcomes=args.include_outcomes)
            for comparison in comparisons
        ],
        "schema_version": "jitc.stage-b-demo/0.1",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
