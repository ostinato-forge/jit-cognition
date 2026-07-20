from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Iterable

from .model import (
    ActionRequest,
    ArtifactEnvelope,
    AuthorizationToken,
    EpistemicObject,
    ObjectKind,
    VerificationResult,
    utc_now,
)
from .runtime import AdmissionDenied, EpistemicRuntime, PermissionDenied


def _digest_json(value: object) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _validate_environment_file(path: str) -> PurePosixPath:
    if not path or "\x00" in path:
        raise ValueError("environment files must be non-empty and NUL-free")
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts or relative == PurePosixPath("."):
        raise ValueError("environment files must remain inside the repository root")
    return relative


def compute_repository_environment_digest(
    repository_root: Path, environment_files: Iterable[str]
) -> str:
    """Hash an explicit, ordered-independent manifest of regular files.

    Directories and symlinks are rejected so the measured set cannot expand
    implicitly or redirect reads outside the repository. The manifest binds
    both file names and bytes; timestamps and other host metadata are excluded.
    """

    root = repository_root.resolve()
    if not root.is_dir():
        raise ValueError("repository_root must be an existing directory")
    file_names = tuple(environment_files)
    if not file_names:
        raise ValueError("environment_files must contain at least one file")
    if len(file_names) != len(set(file_names)):
        raise ValueError("environment_files must be unique")

    manifest: list[dict[str, object]] = []
    for file_name in sorted(file_names):
        relative = _validate_environment_file(file_name)
        lexical_path = root.joinpath(*relative.parts)
        try:
            resolved_path = lexical_path.resolve(strict=True)
        except OSError as exc:
            raise ValueError(f"environment file is unavailable: {file_name}") from exc
        if resolved_path != lexical_path or lexical_path.is_symlink():
            raise ValueError(f"environment file may not use symlinks: {file_name}")
        if root not in resolved_path.parents or not resolved_path.is_file():
            raise ValueError(
                f"environment file must be a regular file in the repository: {file_name}"
            )
        content = resolved_path.read_bytes()
        manifest.append(
            {
                "path": relative.as_posix(),
                "sha256": _digest_bytes(content),
                "size": len(content),
            }
        )
    return _digest_json(
        {
            "files": manifest,
            "format": "jitc.repository-environment/v1",
        }
    )


@dataclass(frozen=True, slots=True)
class CommandSpec:
    command_id: str
    action_id: str
    capability_id: str
    argv: tuple[str, ...]
    cwd: str
    supports_claim_id: str
    dependencies: tuple[str, ...]
    environment_files: tuple[str, ...]
    environment_digest: str
    expected_exit_code: int = 0
    timeout_seconds: int = 120
    output_limit_bytes: int = 32768

    def __post_init__(self) -> None:
        text_fields = (
            self.command_id,
            self.action_id,
            self.capability_id,
            self.cwd,
            self.supports_claim_id,
            self.environment_digest,
        )
        if any(not value or not value.strip() for value in text_fields):
            raise ValueError("command text fields must be non-empty")
        if not self.argv or any(not arg or "\x00" in arg for arg in self.argv):
            raise ValueError("argv must contain non-empty, NUL-free arguments")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("command dependencies must be unique")
        if not self.environment_files:
            raise ValueError("environment_files must contain at least one file")
        if len(self.environment_files) != len(set(self.environment_files)):
            raise ValueError("environment_files must be unique")
        for file_name in self.environment_files:
            _validate_environment_file(file_name)
        digest_algorithm, separator, digest_value = self.environment_digest.partition(":")
        if (
            digest_algorithm != "sha256"
            or separator != ":"
            or len(digest_value) != 64
            or any(character not in "0123456789abcdef" for character in digest_value)
        ):
            raise ValueError("environment_digest must be a lowercase sha256 digest")
        relative = PurePosixPath(self.cwd)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("command cwd must remain inside the repository root")
        if self.timeout_seconds < 1 or self.timeout_seconds > 3600:
            raise ValueError("timeout_seconds must be between 1 and 3600")
        if self.output_limit_bytes < 0:
            raise ValueError("output_limit_bytes cannot be negative")

    @property
    def resource_id(self) -> str:
        action_digest = _digest_json(
            {
                "argv": list(self.argv),
                "capability_id": self.capability_id,
                "command_id": self.command_id,
                "cwd": self.cwd,
                "environment_digest": self.environment_digest,
                "environment_files": list(self.environment_files),
                "timeout_seconds": self.timeout_seconds,
            }
        )
        return f"command://{self.command_id}/{action_digest.removeprefix('sha256:')}"

    @property
    def specification_digest(self) -> str:
        return _digest_json(
            {
                "action_id": self.action_id,
                "argv": list(self.argv),
                "capability_id": self.capability_id,
                "command_id": self.command_id,
                "cwd": self.cwd,
                "dependencies": list(self.dependencies),
                "environment_digest": self.environment_digest,
                "environment_files": list(self.environment_files),
                "expected_exit_code": self.expected_exit_code,
                "output_limit_bytes": self.output_limit_bytes,
                "supports_claim_id": self.supports_claim_id,
                "timeout_seconds": self.timeout_seconds,
            }
        )

    def action_request(self) -> ActionRequest:
        return ActionRequest(
            action_id=self.action_id,
            capability_id=self.capability_id,
            effect="execute",
            resource=self.resource_id,
        )


@dataclass(frozen=True, slots=True)
class CommandExecution:
    command_id: str
    action_id: str
    resource_id: str
    specification_digest: str
    expected_exit_code: int
    return_code: int | None
    timed_out: bool
    stdout_digest: str
    stderr_digest: str
    stdout_preview: str
    stderr_preview: str
    started_at: datetime
    ended_at: datetime
    environment_digest: str
    environment_digest_after: str | None

    @property
    def record_digest(self) -> str:
        return _digest_json(
            {
                "action_id": self.action_id,
                "command_id": self.command_id,
                "ended_at": self.ended_at.isoformat(),
                "environment_digest": self.environment_digest,
                "environment_digest_after": self.environment_digest_after,
                "expected_exit_code": self.expected_exit_code,
                "resource_id": self.resource_id,
                "return_code": self.return_code,
                "specification_digest": self.specification_digest,
                "started_at": self.started_at.isoformat(),
                "stderr_digest": self.stderr_digest,
                "stdout_digest": self.stdout_digest,
                "timed_out": self.timed_out,
            }
        )

    def to_observation(
        self,
        *,
        observation_id: str,
        producer_id: str,
        dependencies: tuple[str, ...],
    ) -> EpistemicObject:
        return EpistemicObject(
            object_id=observation_id,
            kind=ObjectKind.OBSERVATION,
            payload_digest=self.record_digest,
            producer_id=producer_id,
            dependencies=dependencies,
            scope="repository-execution",
        )


class RepositoryCommandExecutor:
    """No-shell command adapter bound to a repository root and token.

    This adapter provides path confinement and exact command-token binding. It
    is not an OS sandbox and does not prevent an allowed executable from using
    the network or accessing resources available to the host process.
    """

    def __init__(
        self,
        *,
        repository_root: Path,
        runtime: EpistemicRuntime,
        allowed_executables: Iterable[str],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.runtime = runtime
        self.allowed_executables = frozenset(allowed_executables)
        if not self.repository_root.is_dir():
            raise ValueError("repository_root must be an existing directory")

    def execute(
        self, spec: CommandSpec, token: AuthorizationToken
    ) -> CommandExecution:
        request = spec.action_request()
        if not self.runtime.validate_authorization(token, request):
            raise PermissionDenied("authorization token does not match command")
        if spec.argv[0] not in self.allowed_executables:
            raise PermissionDenied(
                f"executable is not enabled by the host: {spec.argv[0]}"
            )

        command_cwd = (self.repository_root / spec.cwd).resolve()
        if (
            command_cwd != self.repository_root
            and self.repository_root not in command_cwd.parents
        ):
            raise PermissionDenied("resolved command cwd escapes repository root")
        if not command_cwd.is_dir():
            raise ValueError("command cwd does not exist")

        environment_digest = compute_repository_environment_digest(
            self.repository_root, spec.environment_files
        )
        if environment_digest != spec.environment_digest:
            raise PermissionDenied(
                "measured repository environment does not match command"
            )

        started_at = utc_now()
        timed_out = False
        try:
            completed = subprocess.run(
                list(spec.argv),
                cwd=command_cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                shell=False,
                timeout=spec.timeout_seconds,
            )
            return_code: int | None = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            return_code = None
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            if isinstance(stdout, str):
                stdout = stdout.encode("utf-8", errors="replace")
            if isinstance(stderr, str):
                stderr = stderr.encode("utf-8", errors="replace")
        ended_at = utc_now()
        try:
            environment_digest_after = compute_repository_environment_digest(
                self.repository_root, spec.environment_files
            )
        except (OSError, ValueError):
            environment_digest_after = None

        return CommandExecution(
            command_id=spec.command_id,
            action_id=spec.action_id,
            resource_id=spec.resource_id,
            specification_digest=spec.specification_digest,
            expected_exit_code=spec.expected_exit_code,
            return_code=return_code,
            timed_out=timed_out,
            stdout_digest=_digest_bytes(stdout),
            stderr_digest=_digest_bytes(stderr),
            stdout_preview=stdout[: spec.output_limit_bytes].decode(
                "utf-8", errors="replace"
            ),
            stderr_preview=stderr[: spec.output_limit_bytes].decode(
                "utf-8", errors="replace"
            ),
            started_at=started_at,
            ended_at=ended_at,
            environment_digest=environment_digest,
            environment_digest_after=environment_digest_after,
        )


class ExitCodeVerifier:
    verifier_id = "verifier:exit-code"
    verifier_version = "1"
    authority_id = "runtime:exit-code-verifier"
    mechanism = "process-exit-code"
    implementation = "jitc.exit-code-verifier/v1"

    def verify(
        self,
        *,
        spec: CommandSpec,
        execution: CommandExecution,
        result_id: str,
        observation_id: str,
    ) -> VerificationResult:
        if (
            execution.command_id != spec.command_id
            or execution.resource_id != spec.resource_id
            or execution.specification_digest != spec.specification_digest
        ):
            raise ValueError("execution record does not match command specification")
        return VerificationResult(
            result_id=result_id,
            claim_id=spec.supports_claim_id,
            passed=(
                not execution.timed_out
                and execution.return_code == spec.expected_exit_code
                and execution.environment_digest == spec.environment_digest
                and execution.environment_digest_after == spec.environment_digest
            ),
            verifier_id=self.verifier_id,
            verifier_version=self.verifier_version,
            authority_id=self.authority_id,
            mechanism=self.mechanism,
            implementation=self.implementation,
            data_sources=(spec.resource_id,),
            dependencies=(observation_id,),
            environment_digest=spec.environment_digest,
            issued_at=execution.ended_at,
        )


@dataclass(frozen=True, slots=True)
class RepositoryRun:
    envelope: ArtifactEnvelope
    executions: tuple[CommandExecution, ...]
    runtime: EpistemicRuntime


def execute_repository_commands(
    *,
    runtime: EpistemicRuntime,
    commands: tuple[CommandSpec, ...],
    repository_root: Path,
    allowed_executables: Iterable[str],
) -> RepositoryRun:
    executor = RepositoryCommandExecutor(
        repository_root=repository_root,
        runtime=runtime,
        allowed_executables=allowed_executables,
    )
    verifier = ExitCodeVerifier()
    executions: list[CommandExecution] = []

    for spec in commands:
        token = runtime.authorize_action(spec.action_request())
        execution = executor.execute(spec, token)
        executions.append(execution)
        suffix = execution.record_digest.removeprefix("sha256:")[:16]
        observation_id = f"observation:{spec.command_id}:{suffix}"
        runtime.declare_object(
            execution.to_observation(
                observation_id=observation_id,
                producer_id=spec.capability_id,
                dependencies=spec.dependencies,
            )
        )
        result = verifier.verify(
            spec=spec,
            execution=execution,
            result_id=f"verification:{spec.command_id}:{suffix}",
            observation_id=observation_id,
        )
        runtime.record_verification(result)
        try:
            runtime.admit_claim(spec.supports_claim_id)
        except AdmissionDenied:
            pass

    runtime.assert_invariants()
    return RepositoryRun(
        envelope=runtime.emit_envelope(),
        executions=tuple(executions),
        runtime=runtime,
    )
