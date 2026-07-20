from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from typing import Sequence

from .ecir import load_ecir
from .repository import (
    compute_repository_environment_digest,
    execute_repository_commands,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute an ECIR repository contract"
    )
    parser.add_argument("contract", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--allow-executable",
        action="append",
        help="Exact argv[0] value enabled by the host; repeat as needed",
    )
    parser.add_argument(
        "--measure-environment",
        action="store_true",
        help="Print current command environment digests without executing",
    )
    args = parser.parse_args(argv)

    document = load_ecir(args.contract)
    if args.measure_environment:
        measurements = {
            command.command_id: compute_repository_environment_digest(
                args.repo, command.environment_files
            )
            for command in document.commands
        }
        print(
            json.dumps(
                {"environment_digests": measurements},
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not args.allow_executable:
        parser.error("--allow-executable is required when executing commands")
    runtime = document.instantiate_runtime()
    run = execute_repository_commands(
        runtime=runtime,
        commands=document.commands,
        repository_root=args.repo,
        allowed_executables=args.allow_executable,
    )
    output = {
        "envelope": asdict(run.envelope),
        "executions": [
            {
                "command_id": execution.command_id,
                "environment_digest_after": execution.environment_digest_after,
                "environment_digest_before": execution.environment_digest,
                "environment_stable": (
                    execution.environment_digest
                    == execution.environment_digest_after
                ),
                "record_digest": execution.record_digest,
                "return_code": execution.return_code,
                "stderr_preview": execution.stderr_preview,
                "stdout_preview": execution.stdout_preview,
                "timed_out": execution.timed_out,
            }
            for execution in run.executions
        ],
        "ledger_event_count": len(run.runtime.ledger.events),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if run.envelope.complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
