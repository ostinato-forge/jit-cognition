from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
from typing import Callable, Iterable

from .ledger import AppendOnlyLedger, EventKind
from .model import (
    ActionRequest,
    AdmissionDecision,
    AdmissionPolicy,
    ArtifactEnvelope,
    AuthorizationToken,
    ClaimSpec,
    EpistemicObject,
    Permission,
    RetractionReport,
    TaskContract,
    VerificationResult,
    utc_now,
)


class JITCError(Exception):
    """Base class for rejected runtime transitions."""


class DuplicateIdentifier(JITCError):
    pass


class UnknownIdentifier(JITCError):
    pass


class InvalidDependency(JITCError):
    pass


class CircularSupport(InvalidDependency):
    pass


class AdmissionDenied(JITCError):
    pass


class PermissionDenied(JITCError):
    pass


class InvariantViolation(JITCError):
    pass


class EpistemicRuntime:
    """Reference executable semantics for the small JITC trusted core.

    This class is not a hardened sandbox. It models admission and authorization
    decisions that an enforcing host must honor.
    """

    def __init__(
        self,
        contract: TaskContract,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.contract = contract
        self.ledger = AppendOnlyLedger()
        self._clock = clock
        self._objects: dict[str, EpistemicObject] = {}
        self._claims: dict[str, ClaimSpec] = {}
        self._policies: dict[str, AdmissionPolicy] = {}
        self._verifications: dict[str, VerificationResult] = {}
        self._verifications_by_claim: dict[str, list[str]] = defaultdict(list)
        self._revoked_verifications: set[str] = set()
        self._historically_admitted: set[str] = set()
        self._retracted: set[str] = set()
        self._authorized_actions: dict[str, ActionRequest] = {}
        self._authorization_hashes: dict[str, str] = {}
        self._seen_action_ids: set[str] = set()

    @property
    def retracted_ids(self) -> frozenset[str]:
        return frozenset(self._retracted)

    def register_policy(self, policy: AdmissionPolicy) -> None:
        if policy.policy_id in self._policies:
            raise DuplicateIdentifier(f"policy already exists: {policy.policy_id}")
        self._policies[policy.policy_id] = policy
        self.ledger.append(
            EventKind.POLICY_REGISTERED,
            policy.policy_id,
            {
                "allowed_verifier_ids": list(policy.allowed_verifier_ids),
                "minimum_distinct_data_sources": (
                    policy.minimum_distinct_data_sources
                ),
                "minimum_distinct_implementations": (
                    policy.minimum_distinct_implementations
                ),
                "minimum_distinct_mechanisms": (
                    policy.minimum_distinct_mechanisms
                ),
                "minimum_passes": policy.minimum_passes,
                "require_authority_separation": (
                    policy.require_authority_separation
                ),
                "required_environment_digest": (
                    policy.required_environment_digest
                ),
            },
            self._clock(),
        )

    def declare_object(self, obj: EpistemicObject) -> None:
        self._require_new_node_id(obj.object_id)
        self._require_declared_live_dependencies(obj.dependencies)
        self._objects[obj.object_id] = obj
        self.ledger.append(
            EventKind.OBJECT_DECLARED,
            obj.object_id,
            {
                "dependencies": list(obj.dependencies),
                "kind": obj.kind.value,
                "payload_digest": obj.payload_digest,
                "producer_id": obj.producer_id,
                "scope": obj.scope,
            },
            self._clock(),
        )

    def propose_claim(self, claim: ClaimSpec) -> None:
        self._require_new_node_id(claim.claim_id)
        if claim.policy_id not in self._policies:
            raise UnknownIdentifier(f"unknown policy: {claim.policy_id}")
        self._require_declared_live_dependencies(claim.dependencies)
        self._claims[claim.claim_id] = claim
        self.ledger.append(
            EventKind.CLAIM_PROPOSED,
            claim.claim_id,
            {
                "dependencies": list(claim.dependencies),
                "policy_id": claim.policy_id,
                "proposer_id": claim.proposer_id,
                "scope": claim.scope,
                "statement_digest": claim.statement_digest,
            },
            self._clock(),
        )

    def record_verification(self, result: VerificationResult) -> None:
        if result.result_id in self._verifications:
            raise DuplicateIdentifier(
                f"verification already exists: {result.result_id}"
            )
        if result.claim_id not in self._claims:
            raise UnknownIdentifier(f"unknown claim: {result.claim_id}")
        if result.claim_id in self._retracted:
            raise InvalidDependency(f"claim is retracted: {result.claim_id}")
        self._require_declared_dependencies(result.dependencies)
        now = self._clock()
        if result.issued_at > now:
            raise InvalidDependency("verification cannot be issued in the future")
        for dependency_id in result.dependencies:
            if dependency_id == result.claim_id or self._depends_on(
                dependency_id, result.claim_id
            ):
                raise CircularSupport(
                    "verification support cannot depend on its own claim "
                    f"through {dependency_id}"
                )
        self._verifications[result.result_id] = result
        self._verifications_by_claim[result.claim_id].append(result.result_id)
        self.ledger.append(
            EventKind.VERIFICATION_RECORDED,
            result.result_id,
            {
                "authority_id": result.authority_id,
                "claim_id": result.claim_id,
                "data_sources": list(result.data_sources),
                "dependencies": list(result.dependencies),
                "environment_digest": result.environment_digest,
                "expires_at": (
                    result.expires_at.isoformat()
                    if result.expires_at is not None
                    else None
                ),
                "implementation": result.implementation,
                "issued_at": result.issued_at.isoformat(),
                "mechanism": result.mechanism,
                "passed": result.passed,
                "verifier_id": result.verifier_id,
                "verifier_version": result.verifier_version,
            },
            now,
        )

    def evaluate_claim(
        self, claim_id: str, *, at: datetime | None = None
    ) -> AdmissionDecision:
        if claim_id not in self._claims:
            raise UnknownIdentifier(f"unknown claim: {claim_id}")
        return self._evaluate_claim(
            claim_id, at=at or self._clock(), stack=frozenset()
        )

    def admit_claim(self, claim_id: str) -> AdmissionDecision:
        now = self._clock()
        decision = self.evaluate_claim(claim_id, at=now)
        if not decision.admissible:
            detail = "; ".join(decision.failures)
            raise AdmissionDenied(f"claim {claim_id} is not admissible: {detail}")
        if self.claim_is_established(claim_id, at=now):
            return decision
        self._historically_admitted.add(claim_id)
        self.ledger.append(
            EventKind.CLAIM_ADMITTED,
            claim_id,
            {
                "evidence_ids": list(decision.evidence_ids),
                "policy_id": self._claims[claim_id].policy_id,
            },
            now,
        )
        return decision

    def claim_is_established(
        self,
        claim_id: str,
        *,
        at: datetime | None = None,
        _stack: frozenset[str] = frozenset(),
    ) -> bool:
        if (
            claim_id not in self._claims
            or claim_id not in self._historically_admitted
            or claim_id in self._retracted
            or claim_id in _stack
        ):
            return False
        decision = self._evaluate_claim(
            claim_id,
            at=at or self._clock(),
            stack=_stack | {claim_id},
        )
        return decision.admissible

    def retract(self, target_id: str, reason: str) -> RetractionReport:
        if not reason.strip():
            raise ValueError("retraction reason must be non-empty")
        if target_id in self._verifications:
            return self._revoke_verification(target_id, reason)
        if not self._node_exists(target_id):
            raise UnknownIdentifier(f"unknown object or verification: {target_id}")

        now = self._clock()
        before = {
            claim_id
            for claim_id in self._claims
            if self.claim_is_established(claim_id, at=now)
        }
        closure = self._reverse_dependency_closure(target_id)
        newly_retracted = tuple(sorted(closure - self._retracted))
        for object_id in newly_retracted:
            self._retracted.add(object_id)
            self.ledger.append(
                EventKind.OBJECT_RETRACTED,
                object_id,
                {"reason": reason, "root_id": target_id},
                now,
            )

        after = {
            claim_id
            for claim_id in self._claims
            if self.claim_is_established(claim_id, at=now)
        }
        explicitly_retracted_claims = set(newly_retracted) & set(self._claims)
        invalidated = tuple(sorted((before - after) - explicitly_retracted_claims))
        for claim_id in invalidated:
            self.ledger.append(
                EventKind.CLAIM_INVALIDATED,
                claim_id,
                {"reason": reason, "root_id": target_id},
                now,
            )
        return RetractionReport(target_id, newly_retracted, invalidated)

    def authorize_action(self, request: ActionRequest) -> AuthorizationToken:
        if request.action_id in self._seen_action_ids:
            raise DuplicateIdentifier(f"action already considered: {request.action_id}")
        self._seen_action_ids.add(request.action_id)
        now = self._clock()
        permission = Permission(effect=request.effect, resource=request.resource)
        if permission not in self.contract.permissions:
            self.ledger.append(
                EventKind.ACTION_DENIED,
                request.action_id,
                {
                    "capability_id": request.capability_id,
                    "effect": request.effect,
                    "resource": request.resource,
                },
                now,
            )
            raise PermissionDenied(
                f"contract does not permit {request.effect} on {request.resource}"
            )
        event = self.ledger.append(
            EventKind.ACTION_AUTHORIZED,
            request.action_id,
            {
                "capability_id": request.capability_id,
                "effect": request.effect,
                "resource": request.resource,
            },
            now,
        )
        self._authorized_actions[request.action_id] = request
        self._authorization_hashes[request.action_id] = event.event_hash
        return AuthorizationToken(
            action_id=request.action_id,
            contract_id=self.contract.contract_id,
            effect=request.effect,
            resource=request.resource,
            authorization_event_hash=event.event_hash,
        )

    def validate_authorization(
        self, token: AuthorizationToken, request: ActionRequest
    ) -> bool:
        recorded = self._authorized_actions.get(request.action_id)
        if recorded is None or recorded != request:
            return False
        if token.contract_id != self.contract.contract_id:
            return False
        return (
            token.action_id == request.action_id
            and token.effect == request.effect
            and token.resource == request.resource
            and token.authorization_event_hash
            == self._authorization_hashes.get(request.action_id)
        )

    def emit_envelope(self) -> ArtifactEnvelope:
        now = self._clock()
        established: list[str] = []
        unresolved: list[str] = []
        evidence_ids: set[str] = set()
        for claim_id in self.contract.mandatory_claim_ids:
            if claim_id in self._claims and self.claim_is_established(
                claim_id, at=now
            ):
                established.append(claim_id)
                evidence_ids.update(
                    self.evaluate_claim(claim_id, at=now).evidence_ids
                )
            else:
                unresolved.append(claim_id)

        prior_head = self.ledger.head_hash
        event = self.ledger.append(
            EventKind.ENVELOPE_EMITTED,
            self.contract.contract_id,
            {
                "complete": not unresolved,
                "established_claim_ids": established,
                "evidence_ids": sorted(evidence_ids),
                "prior_ledger_head_hash": prior_head,
                "unresolved_claim_ids": unresolved,
            },
            now,
        )
        return ArtifactEnvelope(
            contract_id=self.contract.contract_id,
            complete=not unresolved,
            established_claim_ids=tuple(established),
            evidence_ids=tuple(sorted(evidence_ids)),
            unresolved_claim_ids=tuple(unresolved),
            ledger_head_hash=event.event_hash,
        )

    def assert_invariants(self) -> None:
        if not self.ledger.verify_integrity():
            raise InvariantViolation("ledger hash chain is invalid")

        for node_id in self._retracted:
            for dependent_id in self._direct_dependents(node_id):
                if dependent_id not in self._retracted:
                    raise InvariantViolation(
                        f"live dependent {dependent_id} of retracted {node_id}"
                    )

        now = self._clock()
        for claim_id in self._claims:
            if self.claim_is_established(claim_id, at=now):
                decision = self.evaluate_claim(claim_id, at=now)
                if not decision.admissible:
                    raise InvariantViolation(
                        f"established claim is not admissible: {claim_id}"
                    )

        for request in self._authorized_actions.values():
            permission = Permission(request.effect, request.resource)
            if permission not in self.contract.permissions:
                raise InvariantViolation(
                    f"unauthorized action stored as authorized: {request.action_id}"
                )
            if request.action_id not in self._authorization_hashes:
                raise InvariantViolation(
                    f"authorized action lacks event binding: {request.action_id}"
                )

        verification_event_sequence = {
            event.subject_id: event.sequence
            for event in self.ledger.events
            if event.kind is EventKind.VERIFICATION_RECORDED
        }
        for event in self.ledger.events:
            if event.kind is not EventKind.CLAIM_ADMITTED:
                continue
            evidence_ids = tuple(event.payload["evidence_ids"])
            if not evidence_ids:
                raise InvariantViolation(
                    f"admission event has no evidence: {event.subject_id}"
                )
            for evidence_id in evidence_ids:
                result = self._verifications.get(evidence_id)
                if result is None or not result.passed:
                    raise InvariantViolation(
                        f"admission references invalid evidence: {evidence_id}"
                    )
                if verification_event_sequence[evidence_id] >= event.sequence:
                    raise InvariantViolation(
                        f"admission predates evidence: {evidence_id}"
                    )

    def _evaluate_claim(
        self,
        claim_id: str,
        *,
        at: datetime,
        stack: frozenset[str],
    ) -> AdmissionDecision:
        claim = self._claims[claim_id]
        policy = self._policies[claim.policy_id]
        failures: list[str] = []

        if claim_id in self._retracted:
            failures.append("claim is retracted")

        unavailable_dependencies = tuple(
            dependency_id
            for dependency_id in claim.dependencies
            if not self._dependency_available(dependency_id, at=at, stack=stack)
        )
        if unavailable_dependencies:
            failures.append(
                "unavailable claim dependencies: "
                + ", ".join(unavailable_dependencies)
            )

        eligible: list[VerificationResult] = []
        for result_id in self._verifications_by_claim.get(claim_id, ()):
            result = self._verifications[result_id]
            if self._verification_is_eligible(
                result, claim=claim, policy=policy, at=at, stack=stack
            ):
                eligible.append(result)

        if len(eligible) < policy.minimum_passes:
            failures.append(
                f"needs {policy.minimum_passes} passing result(s), has {len(eligible)}"
            )

        distinct_mechanisms = {result.mechanism for result in eligible}
        if len(distinct_mechanisms) < policy.minimum_distinct_mechanisms:
            failures.append(
                "insufficient distinct verification mechanisms: "
                f"{len(distinct_mechanisms)}"
            )

        distinct_implementations = {result.implementation for result in eligible}
        if len(distinct_implementations) < policy.minimum_distinct_implementations:
            failures.append(
                "insufficient distinct verifier implementations: "
                f"{len(distinct_implementations)}"
            )

        distinct_sources = {
            source for result in eligible for source in result.data_sources
        }
        if len(distinct_sources) < policy.minimum_distinct_data_sources:
            failures.append(
                "insufficient distinct data sources: "
                f"{len(distinct_sources)}"
            )

        return AdmissionDecision(
            admissible=not failures,
            evidence_ids=tuple(sorted(result.result_id for result in eligible)),
            failures=tuple(failures),
        )

    def _verification_is_eligible(
        self,
        result: VerificationResult,
        *,
        claim: ClaimSpec,
        policy: AdmissionPolicy,
        at: datetime,
        stack: frozenset[str],
    ) -> bool:
        if not result.passed or result.result_id in self._revoked_verifications:
            return False
        if result.issued_at > at:
            return False
        if result.expires_at is not None and at >= result.expires_at:
            return False
        if (
            policy.allowed_verifier_ids
            and result.verifier_id not in policy.allowed_verifier_ids
        ):
            return False
        if (
            policy.required_environment_digest is not None
            and result.environment_digest != policy.required_environment_digest
        ):
            return False
        if (
            policy.require_authority_separation
            and result.authority_id == claim.proposer_id
        ):
            return False
        return all(
            self._dependency_available(
                dependency_id,
                at=at,
                stack=stack,
            )
            for dependency_id in result.dependencies
        )

    def _dependency_available(
        self,
        dependency_id: str,
        *,
        at: datetime,
        stack: frozenset[str],
    ) -> bool:
        if dependency_id in self._retracted:
            return False
        if dependency_id in self._claims:
            return self.claim_is_established(
                dependency_id, at=at, _stack=stack
            )
        return dependency_id in self._objects

    def _revoke_verification(
        self, result_id: str, reason: str
    ) -> RetractionReport:
        now = self._clock()
        before = {
            claim_id
            for claim_id in self._claims
            if self.claim_is_established(claim_id, at=now)
        }
        if result_id not in self._revoked_verifications:
            self._revoked_verifications.add(result_id)
            self.ledger.append(
                EventKind.VERIFICATION_REVOKED,
                result_id,
                {"reason": reason},
                now,
            )
        after = {
            claim_id
            for claim_id in self._claims
            if self.claim_is_established(claim_id, at=now)
        }
        invalidated = tuple(sorted(before - after))
        for claim_id in invalidated:
            self.ledger.append(
                EventKind.CLAIM_INVALIDATED,
                claim_id,
                {"reason": reason, "root_id": result_id},
                now,
            )
        return RetractionReport(result_id, (), invalidated)

    def _require_new_node_id(self, node_id: str) -> None:
        if self._node_exists(node_id) or node_id in self._verifications:
            raise DuplicateIdentifier(f"identifier already exists: {node_id}")

    def _node_exists(self, node_id: str) -> bool:
        return node_id in self._objects or node_id in self._claims

    def _require_declared_dependencies(
        self, dependencies: Iterable[str]
    ) -> None:
        missing = tuple(
            dependency_id
            for dependency_id in dependencies
            if not self._node_exists(dependency_id)
        )
        if missing:
            raise UnknownIdentifier(
                "unknown dependencies: " + ", ".join(sorted(missing))
            )

    def _require_declared_live_dependencies(
        self, dependencies: Iterable[str]
    ) -> None:
        dependencies_tuple = tuple(dependencies)
        self._require_declared_dependencies(dependencies_tuple)
        dead = tuple(
            dependency_id
            for dependency_id in dependencies_tuple
            if dependency_id in self._retracted
        )
        if dead:
            raise InvalidDependency(
                "retracted dependencies: " + ", ".join(sorted(dead))
            )

    def _node_dependencies(self, node_id: str) -> tuple[str, ...]:
        if node_id in self._objects:
            return self._objects[node_id].dependencies
        if node_id in self._claims:
            return self._claims[node_id].dependencies
        raise UnknownIdentifier(f"unknown node: {node_id}")

    def _depends_on(self, node_id: str, possible_ancestor: str) -> bool:
        queue = deque([node_id])
        visited: set[str] = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for dependency_id in self._node_dependencies(current):
                if dependency_id == possible_ancestor:
                    return True
                queue.append(dependency_id)
        return False

    def _direct_dependents(self, node_id: str) -> set[str]:
        dependents: set[str] = set()
        for candidate_id in (*self._objects.keys(), *self._claims.keys()):
            if node_id in self._node_dependencies(candidate_id):
                dependents.add(candidate_id)
        return dependents

    def _reverse_dependency_closure(self, root_id: str) -> set[str]:
        closure: set[str] = set()
        queue = deque([root_id])
        while queue:
            current = queue.popleft()
            if current in closure:
                continue
            closure.add(current)
            queue.extend(sorted(self._direct_dependents(current)))
        return closure
