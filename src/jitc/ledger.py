from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class EventKind(str, Enum):
    POLICY_REGISTERED = "policy_registered"
    OBJECT_DECLARED = "object_declared"
    CLAIM_PROPOSED = "claim_proposed"
    VERIFICATION_RECORDED = "verification_recorded"
    VERIFICATION_REVOKED = "verification_revoked"
    CLAIM_ADMITTED = "claim_admitted"
    CLAIM_INVALIDATED = "claim_invalidated"
    OBJECT_RETRACTED = "object_retracted"
    ACTION_AUTHORIZED = "action_authorized"
    ACTION_DENIED = "action_denied"
    ENVELOPE_EMITTED = "envelope_emitted"


@dataclass(frozen=True, slots=True)
class LedgerEvent:
    sequence: int
    kind: EventKind
    subject_id: str
    payload_json: str
    recorded_at: str
    previous_hash: str
    event_hash: str

    @property
    def payload(self) -> dict[str, Any]:
        value = json.loads(self.payload_json)
        if not isinstance(value, dict):
            raise ValueError("ledger payload must decode to an object")
        return value


class AppendOnlyLedger:
    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []

    @property
    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    @property
    def head_hash(self) -> str:
        if not self._events:
            return self.GENESIS_HASH
        return self._events[-1].event_hash

    def append(
        self,
        kind: EventKind,
        subject_id: str,
        payload: Mapping[str, Any],
        recorded_at: datetime,
    ) -> LedgerEvent:
        payload_json = json.dumps(
            dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        event = self._build_event(
            sequence=len(self._events),
            kind=kind,
            subject_id=subject_id,
            payload_json=payload_json,
            recorded_at=recorded_at.isoformat(),
            previous_hash=self.head_hash,
        )
        self._events.append(event)
        return event

    def verify_integrity(self) -> bool:
        previous_hash = self.GENESIS_HASH
        for sequence, event in enumerate(self._events):
            if event.sequence != sequence or event.previous_hash != previous_hash:
                return False
            rebuilt = self._build_event(
                sequence=event.sequence,
                kind=event.kind,
                subject_id=event.subject_id,
                payload_json=event.payload_json,
                recorded_at=event.recorded_at,
                previous_hash=event.previous_hash,
            )
            if rebuilt.event_hash != event.event_hash:
                return False
            previous_hash = event.event_hash
        return True

    @staticmethod
    def _build_event(
        *,
        sequence: int,
        kind: EventKind,
        subject_id: str,
        payload_json: str,
        recorded_at: str,
        previous_hash: str,
    ) -> LedgerEvent:
        canonical = json.dumps(
            {
                "kind": kind.value,
                "payload_json": payload_json,
                "previous_hash": previous_hash,
                "recorded_at": recorded_at,
                "sequence": sequence,
                "subject_id": subject_id,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return LedgerEvent(
            sequence=sequence,
            kind=kind,
            subject_id=subject_id,
            payload_json=payload_json,
            recorded_at=recorded_at,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
