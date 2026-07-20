from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from jitc import ECIRError, load_ecir, parse_ecir


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_example_ecir_loads_and_binds_permission_to_command_content() -> None:
    document = load_ecir(
        PROJECT_ROOT / "examples" / "kernel-self-check.ecir.json"
    )

    assert document.version == "0.1"
    assert len(document.commands) == 1
    command = document.commands[0]
    assert document.contract.permissions[0].resource == command.resource_id

    changed = replace(command, argv=("python3", "-m", "pytest", "--collect-only"))
    assert changed.resource_id != command.resource_id


def test_ecir_rejects_unknown_fields() -> None:
    with pytest.raises(ECIRError, match="unknown document fields"):
        parse_ecir(
            {
                "ecir_version": "0.1",
                "contract": {
                    "contract_id": "contract",
                    "mandatory_claim_ids": [],
                },
                "policies": [],
                "objects": [],
                "claims": [],
                "commands": [],
                "permissions": [],
                "hidden_magic": True,
            }
        )


def test_ecir_rejects_undeclared_mandatory_claim() -> None:
    with pytest.raises(ECIRError, match="mandatory claims are not declared"):
        parse_ecir(
            {
                "ecir_version": "0.1",
                "contract": {
                    "contract_id": "contract",
                    "mandatory_claim_ids": ["missing"],
                },
                "policies": [],
                "objects": [],
                "claims": [],
                "commands": [],
                "permissions": [],
            }
        )


def test_ecir_rejects_environment_digest_without_matching_object() -> None:
    raw = json.loads(
        (PROJECT_ROOT / "examples" / "kernel-self-check.ecir.json").read_text(
            encoding="utf-8"
        )
    )
    raw["objects"][0]["payload_digest"] = "sha256:" + "1" * 64

    with pytest.raises(ECIRError, match="matching environment object"):
        parse_ecir(raw)
