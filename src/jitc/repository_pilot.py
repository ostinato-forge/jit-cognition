from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from typing import Mapping, Sequence

from .experiment import (
    Adjudication,
    CapabilityRegistry,
    ConditionReport,
    EvaluationCase,
    ExperimentConfig,
    FunctionProposer,
    InterventionComparison,
    ManualCapability,
    NullProposer,
    Proposer,
    TaskInstance,
    evaluate_condition,
    evaluate_intervention_curve,
)


def _repository_path(value: str) -> PurePosixPath:
    if not value or "\x00" in value:
        raise ValueError("repository paths must be non-empty and NUL-free")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path == PurePosixPath(".")
        or path.as_posix() != value
    ):
        raise ValueError("repository paths must be canonical relative paths")
    return path


def _validate_files(
    files: tuple[tuple[str, str], ...], *, name: str
) -> None:
    if not files:
        raise ValueError(f"{name} must contain at least one file")
    paths = tuple(path for path, _ in files)
    if len(paths) != len(set(paths)):
        raise ValueError(f"{name} paths must be unique")
    for path, content in files:
        _repository_path(path)
        if not isinstance(content, str):
            raise ValueError(f"{name} contents must be strings")


@dataclass(frozen=True, slots=True)
class RepositoryFixture:
    fixture_id: str
    files: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.fixture_id or not self.fixture_id.strip():
            raise ValueError("fixture_id must be non-empty")
        _validate_files(self.files, name="fixture files")

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            {"files": self.files, "fixture_id": self.fixture_id},
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        return "sha256:" + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

    def read(self, path: str) -> str:
        try:
            return dict(self.files)[path]
        except KeyError as exc:
            raise ValueError(f"fixture lacks file: {path}") from exc

    def materialize(self, root: Path) -> None:
        for relative_name, content in self.files:
            relative = _repository_path(relative_name)
            destination = root.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")


@dataclass(frozen=True, slots=True)
class FileChange:
    path: str
    content: str

    def __post_init__(self) -> None:
        _repository_path(self.path)


@dataclass(frozen=True, slots=True)
class PatchSet:
    changes: tuple[FileChange, ...] = ()

    def __post_init__(self) -> None:
        paths = tuple(change.path for change in self.changes)
        if len(paths) != len(set(paths)):
            raise ValueError("a patch may change each path at most once")

    def to_json(self) -> str:
        return json.dumps(
            {
                "changes": [
                    {"content": change.content, "path": change.path}
                    for change in self.changes
                ]
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, value: str) -> PatchSet:
        try:
            raw = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("candidate patch is not valid JSON") from exc
        if not isinstance(raw, dict) or set(raw) != {"changes"}:
            raise ValueError("candidate patch must contain only changes")
        changes = raw["changes"]
        if not isinstance(changes, list):
            raise ValueError("candidate patch changes must be an array")
        parsed: list[FileChange] = []
        for item in changes:
            if not isinstance(item, dict) or set(item) != {"content", "path"}:
                raise ValueError("patch changes require path and content")
            path = item["path"]
            content = item["content"]
            if not isinstance(path, str) or not isinstance(content, str):
                raise ValueError("patch path and content must be strings")
            parsed.append(FileChange(path=path, content=content))
        return cls(tuple(parsed))

    def apply(self, root: Path) -> None:
        repository_root = root.resolve()
        for change in self.changes:
            relative = _repository_path(change.path)
            destination = repository_root.joinpath(*relative.parts)
            resolved = destination.resolve(strict=True)
            if (
                resolved != destination
                or repository_root not in resolved.parents
                or destination.is_symlink()
                or not destination.is_file()
            ):
                raise ValueError(
                    f"patch target must be an existing regular file: {change.path}"
                )
            destination.write_text(change.content, encoding="utf-8")


@dataclass(frozen=True, slots=True)
class HiddenRepositoryCase:
    evaluation_case: EvaluationCase
    fixture: RepositoryFixture
    expected_files: tuple[tuple[str, str], ...]
    hidden_argv: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_files(self.expected_files, name="expected files")
        if set(dict(self.expected_files)) != set(dict(self.fixture.files)):
            raise ValueError(
                "expected files must describe the complete fixture snapshot"
            )
        fixture_id = self.evaluation_case.task.attribute("fixture_id")
        if fixture_id != self.fixture.fixture_id:
            raise ValueError("task fixture_id does not match hidden fixture")
        if not self.hidden_argv or any(not value for value in self.hidden_argv):
            raise ValueError("hidden_argv must contain non-empty arguments")


class RepositoryAdjudicator:
    """Materialize, patch, compare, and execute a trusted hidden check.

    Patched code can execute through hidden_argv. This pilot therefore accepts
    only repository fixtures and candidate generators trusted by the operator;
    it is not a sandbox for arbitrary patches.
    """

    def __init__(self, cases: Sequence[HiddenRepositoryCase]) -> None:
        case_tuple = tuple(cases)
        task_ids = tuple(
            case.evaluation_case.task.task_id for case in case_tuple
        )
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("hidden repository task identifiers must be unique")
        self._cases = {
            case.evaluation_case.task.task_id: case for case in case_tuple
        }

    def adjudicate(
        self, case: EvaluationCase, candidate: str
    ) -> Adjudication:
        hidden = self._cases.get(case.task.task_id)
        if hidden is None:
            return Adjudication(valid=False, utility=0.0)
        try:
            patch = PatchSet.from_json(candidate)
            with tempfile.TemporaryDirectory(
                prefix="jitc-repository-pilot-"
            ) as directory:
                root = Path(directory)
                hidden.fixture.materialize(root)
                patch.apply(root)
                actual_files = tuple(
                    sorted(
                        (
                            path.relative_to(root).as_posix(),
                            path.read_text(encoding="utf-8"),
                        )
                        for path in root.rglob("*")
                        if path.is_file()
                    )
                )
                if actual_files != tuple(sorted(hidden.expected_files)):
                    return Adjudication(valid=False, utility=0.0)
                completed = subprocess.run(
                    list(hidden.hidden_argv),
                    cwd=root,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    shell=False,
                    timeout=5,
                )
        except (OSError, subprocess.SubprocessError, ValueError):
            return Adjudication(valid=False, utility=0.0)
        valid = completed.returncode == 0
        return Adjudication(valid=valid, utility=1.0 if valid else 0.0)


class SnapshotRetrievalProposer:
    def __init__(
        self,
        *,
        fixtures: Mapping[str, RepositoryFixture],
        memory: Mapping[str, str],
        proposer_id: str = "baseline:snapshot-retrieval",
        call_cost_units: float = 0.08,
        lifecycle_cost_units: float = 4.0,
    ) -> None:
        self.proposer_id = proposer_id
        self.call_cost_units = call_cost_units
        self.lifecycle_cost_units = lifecycle_cost_units
        self._fixtures = dict(fixtures)
        self._memory = dict(memory)

    def propose(self, task: TaskInstance) -> str | None:
        fixture_id = task.attribute("fixture_id")
        if fixture_id is None or fixture_id not in self._fixtures:
            return None
        return self._memory.get(self._fixtures[fixture_id].digest)


@dataclass(frozen=True, slots=True)
class RepositoryPilotInputs:
    cases: tuple[EvaluationCase, ...]
    registries: tuple[CapabilityRegistry, ...]
    original_proposer: FunctionProposer
    null_proposer: NullProposer
    workflow_proposer: FunctionProposer
    retrieval_proposer: SnapshotRetrievalProposer
    adjudicator: RepositoryAdjudicator
    config: ExperimentConfig
    benchmark_definition_digest: str


@dataclass(frozen=True, slots=True)
class RepositoryPilotReport:
    intervention_curve: tuple[InterventionComparison, ...]
    baselines: tuple[ConditionReport, ...]
    benchmark_definition_digest: str

    def to_dict(self, *, include_outcomes: bool = False) -> dict[str, object]:
        return {
            "baselines": [
                baseline.to_dict(include_outcomes=include_outcomes)
                for baseline in self.baselines
            ],
            "claim_boundary": (
                "Constructed trusted-fixture pilot with oracle family labels; "
                "not a real-repository or untrusted-code result."
            ),
            "benchmark_definition_digest": self.benchmark_definition_digest,
            "intervention_curve": [
                comparison.to_dict(include_outcomes=include_outcomes)
                for comparison in self.intervention_curve
            ],
            "schema_version": "jitc.repository-pilot/0.1",
        }


def _task(
    task_id: str,
    family_id: str,
    fixture_id: str,
    *,
    environment: tuple[tuple[str, str], ...] = (),
) -> EvaluationCase:
    return EvaluationCase(
        TaskInstance(
            task_id=task_id,
            family_id=family_id,
            attributes=(("fixture_id", fixture_id),),
            environment=environment,
        ),
        expected_output="hidden-repository-adjudication",
    )


def _rename_key(value: object) -> object:
    if isinstance(value, dict):
        return {
            ("request_timeout_ms" if key == "timeout_ms" else key): (
                _rename_key(child)
            )
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_rename_key(child) for child in value]
    return value


def _config_v1_handler(
    fixtures: Mapping[str, RepositoryFixture],
):
    def handler(task: TaskInstance) -> str:
        fixture = _fixture_for_task(task, fixtures)
        transformed = _rename_key(json.loads(fixture.read("settings.json")))
        content = json.dumps(transformed, indent=2, sort_keys=True) + "\n"
        return PatchSet((FileChange("settings.json", content),)).to_json()

    return handler


def _config_general_handler(
    fixtures: Mapping[str, RepositoryFixture],
):
    v1_handler = _config_v1_handler(fixtures)

    def handler(task: TaskInstance) -> str:
        if task.environment_value("config_schema") == "v2":
            return PatchSet().to_json()
        return v1_handler(task)

    return handler


def _api_handler(fixtures: Mapping[str, RepositoryFixture]):
    def handler(task: TaskInstance) -> str:
        fixture = _fixture_for_task(task, fixtures)
        original = fixture.read("app.py")
        migrated = original.replace("legacy_api", "modern_api")
        if migrated == original:
            raise ValueError("fixture does not use legacy_api")
        return PatchSet((FileChange("app.py", migrated),)).to_json()

    return handler


def _delimiter_handler(fixtures: Mapping[str, RepositoryFixture]):
    def handler(task: TaskInstance) -> str:
        fixture = _fixture_for_task(task, fixtures)
        original = fixture.read("report.py")
        migrated = original.replace('DELIMITER = ","', 'DELIMITER = "|"')
        if migrated == original:
            raise ValueError("fixture does not declare the expected delimiter")
        return PatchSet((FileChange("report.py", migrated),)).to_json()

    return handler


def _fixture_for_task(
    task: TaskInstance, fixtures: Mapping[str, RepositoryFixture]
) -> RepositoryFixture:
    fixture_id = task.attribute("fixture_id")
    if fixture_id is None or fixture_id not in fixtures:
        raise ValueError("task refers to an unknown fixture")
    return fixtures[fixture_id]


def _support_files() -> tuple[tuple[str, str], ...]:
    return (
        (
            "legacy_api.py",
            'def fetch(value):\n    return f"legacy:{value}"\n',
        ),
        (
            "modern_api.py",
            'def fetch(value):\n    return f"modern:{value}"\n',
        ),
    )


def _definition_digest(
    *,
    hidden_cases: tuple[HiddenRepositoryCase, ...],
    registries: tuple[CapabilityRegistry, ...],
    proposers: tuple[Proposer, ...],
    config: ExperimentConfig,
) -> str:
    definition = {
        "config": {
            "lifecycle_amortization_tasks": (
                config.lifecycle_amortization_tasks
            ),
            "lookup_cost_units": config.lookup_cost_units,
            "max_online_cost_per_task": config.max_online_cost_per_task,
            "verification_cost_units": config.verification_cost_units,
        },
        "proposers": [
            {
                "call_cost_units": proposer.call_cost_units,
                "lifecycle_cost_units": proposer.lifecycle_cost_units,
                "proposer_id": proposer.proposer_id,
            }
            for proposer in proposers
        ],
        "registries": [
            {
                "capabilities": [
                    {
                        "capability_id": capability.capability_id,
                        "execution_cost_units": (
                            capability.execution_cost_units
                        ),
                        "family_id": capability.family_id,
                        "maintenance_cost_units": (
                            capability.maintenance_cost_units
                        ),
                        "promotion_cost_units": (
                            capability.promotion_cost_units
                        ),
                        "required_attributes": (
                            capability.required_attributes
                        ),
                        "required_environment": (
                            capability.required_environment
                        ),
                        "validation_cost_units": (
                            capability.validation_cost_units
                        ),
                    }
                    for capability in registry.capabilities
                ],
                "checkpoint_id": registry.checkpoint_id,
            }
            for registry in registries
        ],
        "tasks": [
            {
                "attributes": hidden.evaluation_case.task.attributes,
                "environment": hidden.evaluation_case.task.environment,
                "expected_files": hidden.expected_files,
                "family_id": hidden.evaluation_case.task.family_id,
                "fixture": hidden.fixture.files,
                "fixture_id": hidden.fixture.fixture_id,
                "hidden_argv": (
                    ("<python>",) + hidden.hidden_argv[1:]
                    if hidden.hidden_argv[0] == sys.executable
                    else hidden.hidden_argv
                ),
                "task_id": hidden.evaluation_case.task.task_id,
            }
            for hidden in hidden_cases
        ],
    }
    canonical = json.dumps(
        definition,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_repository_pilot() -> RepositoryPilotInputs:
    nested_input = (
        '{\n  "service": {\n    "timeout_ms": 3000,\n'
        '    "retries": 2\n  }\n}\n'
    )
    nested_expected = (
        '{\n  "service": {\n    "request_timeout_ms": 3000,\n'
        '    "retries": 2\n  }\n}\n'
    )
    flat_input = '{"retries":4,"timeout_ms":1500}\n'
    flat_expected = (
        '{\n  "request_timeout_ms": 1500,\n  "retries": 4\n}\n'
    )
    shifted_input = (
        '{\n  "telemetry": {\n    "timeout_ms": 500\n  }\n}\n'
    )
    direct_app = (
        'from legacy_api import fetch\n\nRESULT = fetch("x")\n'
    )
    direct_expected = (
        'from modern_api import fetch\n\nRESULT = fetch("x")\n'
    )
    alias_app = (
        'import legacy_api as api\n\nRESULT = api.fetch("y")\n'
    )
    alias_expected = (
        'import modern_api as api\n\nRESULT = api.fetch("y")\n'
    )
    report_input = (
        'DELIMITER = ","\n\n'
        "def render(values):\n"
        "    return DELIMITER.join(values)\n"
    )
    report_expected = report_input.replace(
        'DELIMITER = ","', 'DELIMITER = "|"'
    )

    fixtures_tuple = (
        RepositoryFixture(
            "fixture:config-nested",
            (("settings.json", nested_input),),
        ),
        RepositoryFixture(
            "fixture:config-flat",
            (("settings.json", flat_input),),
        ),
        RepositoryFixture(
            "fixture:config-shifted",
            (("settings.json", shifted_input),),
        ),
        RepositoryFixture(
            "fixture:api-direct",
            (("app.py", direct_app),) + _support_files(),
        ),
        RepositoryFixture(
            "fixture:api-alias",
            (("app.py", alias_app),) + _support_files(),
        ),
        RepositoryFixture(
            "fixture:novel-delimiter",
            (("report.py", report_input),),
        ),
    )
    fixtures = {fixture.fixture_id: fixture for fixture in fixtures_tuple}

    cases = (
        _task(
            "repo:config-nested",
            "migrate-config-timeout",
            "fixture:config-nested",
            environment=(("config_schema", "v1"),),
        ),
        _task(
            "repo:config-flat",
            "migrate-config-timeout",
            "fixture:config-flat",
            environment=(("config_schema", "v1"),),
        ),
        _task(
            "repo:config-shifted-near-match",
            "migrate-config-timeout",
            "fixture:config-shifted",
            environment=(("config_schema", "v2"),),
        ),
        _task(
            "repo:api-direct",
            "migrate-api-provider",
            "fixture:api-direct",
            environment=(("provider_contract", "v1"),),
        ),
        _task(
            "repo:api-alias",
            "migrate-api-provider",
            "fixture:api-alias",
            environment=(("provider_contract", "v1"),),
        ),
        _task(
            "repo:novel-delimiter",
            "change-report-delimiter",
            "fixture:novel-delimiter",
        ),
    )
    by_task_id = {case.task.task_id: case for case in cases}
    hidden_cases = (
        HiddenRepositoryCase(
            by_task_id["repo:config-nested"],
            fixtures["fixture:config-nested"],
            (("settings.json", nested_expected),),
            (
                sys.executable,
                "-c",
                (
                    "import json; d=json.load(open('settings.json')); "
                    "s=d['service']; assert s['request_timeout_ms']==3000; "
                    "assert 'timeout_ms' not in s"
                ),
            ),
        ),
        HiddenRepositoryCase(
            by_task_id["repo:config-flat"],
            fixtures["fixture:config-flat"],
            (("settings.json", flat_expected),),
            (
                sys.executable,
                "-c",
                (
                    "import json; d=json.load(open('settings.json')); "
                    "assert d['request_timeout_ms']==1500; "
                    "assert 'timeout_ms' not in d"
                ),
            ),
        ),
        HiddenRepositoryCase(
            by_task_id["repo:config-shifted-near-match"],
            fixtures["fixture:config-shifted"],
            (("settings.json", shifted_input),),
            (
                sys.executable,
                "-c",
                (
                    "import json; d=json.load(open('settings.json')); "
                    "assert d['telemetry']['timeout_ms']==500; "
                    "assert 'request_timeout_ms' not in d['telemetry']"
                ),
            ),
        ),
        HiddenRepositoryCase(
            by_task_id["repo:api-direct"],
            fixtures["fixture:api-direct"],
            (("app.py", direct_expected),) + _support_files(),
            (
                sys.executable,
                "-c",
                "import app; assert app.RESULT == 'modern:x'",
            ),
        ),
        HiddenRepositoryCase(
            by_task_id["repo:api-alias"],
            fixtures["fixture:api-alias"],
            (("app.py", alias_expected),) + _support_files(),
            (
                sys.executable,
                "-c",
                "import app; assert app.RESULT == 'modern:y'",
            ),
        ),
        HiddenRepositoryCase(
            by_task_id["repo:novel-delimiter"],
            fixtures["fixture:novel-delimiter"],
            (("report.py", report_expected),),
            (
                sys.executable,
                "-c",
                "import report; assert report.render(['a','b']) == 'a|b'",
            ),
        ),
    )
    adjudicator = RepositoryAdjudicator(hidden_cases)

    config_v1 = _config_v1_handler(fixtures)
    config_general = _config_general_handler(fixtures)
    api = _api_handler(fixtures)
    delimiter = _delimiter_handler(fixtures)
    config_capability = ManualCapability(
        capability_id="capability:repository-config-v1",
        family_id="migrate-config-timeout",
        implementation=config_v1,
        required_environment=(("config_schema", "v1"),),
        execution_cost_units=0.15,
        promotion_cost_units=3.0,
        validation_cost_units=4.0,
        maintenance_cost_units=1.0,
    )
    api_capability = ManualCapability(
        capability_id="capability:repository-api-v1",
        family_id="migrate-api-provider",
        implementation=api,
        required_environment=(("provider_contract", "v1"),),
        execution_cost_units=0.15,
        promotion_cost_units=3.5,
        validation_cost_units=4.5,
        maintenance_cost_units=1.0,
    )
    registries = (
        CapabilityRegistry("repository:0-cold"),
        CapabilityRegistry(
            "repository:1-config", (config_capability,)
        ),
        CapabilityRegistry(
            "repository:2-config-api",
            (config_capability, api_capability),
        ),
    )
    original = FunctionProposer(
        proposer_id="proposer:repository-strong",
        handlers={
            "migrate-config-timeout": config_general,
            "migrate-api-provider": api,
            "change-report-delimiter": delimiter,
        },
        call_cost_units=1.0,
    )
    null = NullProposer(
        proposer_id="proposer:repository-null",
        call_cost_units=0.05,
    )
    workflow = FunctionProposer(
        proposer_id="baseline:deterministic-workflow",
        handlers={
            "migrate-config-timeout": config_general,
            "migrate-api-provider": api,
        },
        call_cost_units=0.2,
        lifecycle_cost_units=12.0,
    )
    seed_tasks = (
        by_task_id["repo:config-nested"].task,
        by_task_id["repo:api-direct"].task,
    )
    seed_handlers = {
        "migrate-config-timeout": config_general,
        "migrate-api-provider": api,
    }
    memory = {
        _fixture_for_task(task, fixtures).digest: seed_handlers[
            task.family_id
        ](task)
        for task in seed_tasks
    }
    retrieval = SnapshotRetrievalProposer(
        fixtures=fixtures,
        memory=memory,
    )
    config = ExperimentConfig(lifecycle_amortization_tasks=60)
    definition_digest = _definition_digest(
        hidden_cases=hidden_cases,
        registries=registries,
        proposers=(original, null, workflow, retrieval),
        config=config,
    )
    return RepositoryPilotInputs(
        cases=cases,
        registries=registries,
        original_proposer=original,
        null_proposer=null,
        workflow_proposer=workflow,
        retrieval_proposer=retrieval,
        adjudicator=adjudicator,
        config=config,
        benchmark_definition_digest=definition_digest,
    )


def run_repository_pilot() -> RepositoryPilotReport:
    inputs = build_repository_pilot()
    curve = evaluate_intervention_curve(
        cases=inputs.cases,
        registries=inputs.registries,
        original_proposer=inputs.original_proposer,
        intervention_proposer=inputs.null_proposer,
        adjudicator=inputs.adjudicator,
        config=inputs.config,
    )
    baseline_specs: tuple[tuple[str, Proposer], ...] = (
        ("baseline:direct-strong", inputs.original_proposer),
        ("baseline:deterministic-workflow", inputs.workflow_proposer),
        ("baseline:snapshot-retrieval", inputs.retrieval_proposer),
        ("baseline:null", inputs.null_proposer),
    )
    baselines = tuple(
        evaluate_condition(
            condition_id=condition_id,
            cases=inputs.cases,
            registry=inputs.registries[0],
            proposer=proposer,
            adjudicator=inputs.adjudicator,
            config=inputs.config,
        )
        for condition_id, proposer in baseline_specs
    )
    return RepositoryPilotReport(
        curve,
        baselines,
        inputs.benchmark_definition_digest,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the trusted-fixture JITC repository reuse pilot"
    )
    parser.add_argument(
        "--include-outcomes",
        action="store_true",
        help="Include task-level patch outcomes in the JSON report",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_repository_pilot().to_dict(
                include_outcomes=args.include_outcomes
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
