# Formal Core

## 1. Purpose and boundary

This document specifies the smallest JITC kernel for which meaningful
conditional guarantees can be stated. It does not formalize natural-language
intent, arbitrary planning, program synthesis, verifier construction, or
open-world truth.

The kernel is an admission and dependency machine. Untrusted components may
submit objects and verifier results. Only kernel transitions determine current
admissibility, action authorization, and emitted evidence envelopes.

## 2. State

Let a runtime state be:

\[
S = \langle C, O, K, V, A, R, L \rangle
\]

where:

- \(C\) is an immutable task contract;
- \(O\) is a set of immutable epistemic objects;
- \(K\) is a set of immutable claim specifications;
- \(V\) is a set of verifier-result records;
- \(A\) is the historical set of claim-admission events;
- \(R\) is the set of explicitly retracted objects;
- \(L\) is an append-only hash-linked event ledger.

Each object and claim has a stable identifier. New versions receive new
identifiers; retracted identifiers are never silently reactivated.

The declared dependency relation \(x \prec y\) means that \(y\) depends on
\(x\). Dependencies may refer only to objects already declared, so the declared
graph is acyclic by construction.

## 3. Separate dimensions

The kernel intentionally does not define a universal epistemic lattice.

An object has a kind:

\[
\operatorname{kind}(x) \in
\{\text{observation},\text{assumption},\text{claim},\text{artifact}\}.
\]

A claim has proposal provenance and an admission policy. Explicit retraction
and current admission are independent predicates:

\[
\operatorname{live}_S(x) \equiv x \notin R
\]

\[
\operatorname{historicallyAdmitted}_S(k) \equiv
\exists e \in L:\ e = \operatorname{Admit}(k,\ldots)
\]

Current establishment is recomputed rather than stored as an eternal bit.

## 4. Verifier results

A verifier result \(v\) contains:

\[
v = \langle
id, claim, pass, verifier, version, authority, mechanism,
implementation, sources, dependencies, environment, issued, expiry
\rangle .
\]

It is eligible at time \(t\) only when:

1. it records a pass;
2. it has been issued and has not expired;
3. its verifier is permitted by the claim's policy;
4. its environment matches any policy requirement;
5. all of its dependencies are currently available; and
6. its authority differs from the proposer when separation is required.

Availability is recursive:

- a non-claim dependency is available when it is live;
- a claim dependency is available when that claim is currently established.

Verifier dependencies may not introduce a path back to the claim being
verified. This prevents circular evidence.

## 5. Admission policies

An admission policy is a deterministic predicate over eligible verifier
results. The prototype supports:

- a minimum number of passing results;
- an allow-list of verifier identities;
- a required environment digest;
- minimum counts of distinct mechanisms;
- minimum counts of distinct implementations;
- minimum counts of distinct data sources; and
- proposer/verifier authority separation.

These counts are explicit approximations to independence. They do not prove
statistical or causal independence.

For claim \(k\), policy \(p_k\), ledger \(L\), and time \(t\):

\[
\operatorname{support}(k,S,t)
= \{v \in V \mid \operatorname{eligible}(v,k,S,t)\}
\]

\[
\operatorname{admissible}(k,S,t)
\equiv p_k(\operatorname{support}(k,S,t))
\land \bigwedge_{d \in deps(k)} \operatorname{available}(d,S,t).
\]

A claim is currently established exactly when it has a historical admission,
is live, and remains admissible:

\[
\operatorname{established}(k,S,t)
\equiv
\operatorname{historicallyAdmitted}(k)
\land \operatorname{live}(k)
\land \operatorname{admissible}(k,S,t).
\]

This definition means expiration or dependency loss can make an admitted claim
currently unavailable without erasing its history.

## 6. Transitions

The public kernel supports:

- DECLARE-OBJECT;
- PROPOSE-CLAIM;
- RECORD-VERIFIER-RESULT;
- ADMIT-CLAIM;
- RETRACT;
- AUTHORIZE-ACTION; and
- EMIT-ENVELOPE.

### 6.1 Declaration

An object or claim may be declared only when its identifier is unused and all
declared dependencies already exist. This establishes acyclicity by insertion
order.

### 6.2 Admission

ADMIT-CLAIM may append an admission event only when
\(\operatorname{admissible}(k,S,t)\) is true. The event records the exact
verifier-result identifiers used by the policy decision.

There is no public operation that directly assigns an established status.

### 6.3 Retraction and invalidation

RETRACT(x) appends retraction events for \(x\) and every node in the reverse
transitive closure of the declared dependency relation.

Separately, any claim whose current support becomes inadequate is no longer
established, even if it is not explicitly retracted. Implementations may append
an invalidation event to explain the transition. This distinction matters:

- retraction says an object itself has been withdrawn;
- invalidation says its current admission predicate no longer holds.

### 6.4 Action authorization

An action request names an exact effect and resource. The kernel issues an
authorization token only if that pair occurs in the contract's immutable
permission set.

The guarantee applies only if every effectful adapter requires a genuine token
and no capability can escape the enforcement boundary.

### 6.5 Emission

EMIT-ENVELOPE recomputes current establishment for every mandatory claim. A
complete envelope is emitted only when all are established. Otherwise the
runtime emits a typed unresolved envelope and must not label missing claims as
established.

## 7. Conditional theorems

### Theorem 1: Admission safety

Assume:

1. ledger events can be appended only through the public kernel transitions;
2. policy evaluation is implemented according to this specification; and
3. registered policy definitions are immutable during a run.

Then every ADMIT-CLAIM event was accompanied by a policy-satisfying set of
eligible verifier results at the event time.

**Proof sketch.** The initial ledger contains no admission events. The only
transition that appends an admission event is ADMIT-CLAIM. Its precondition is
the admission predicate, and it records the satisfying evidence identifiers.
All other transitions preserve the claim. Induction over ledger length gives
the result.

### Theorem 2: No proposer self-attestation under separation

If a claim policy requires authority separation, no verifier result whose
authority equals the claim's proposer contributes to the admission predicate.

**Proof sketch.** Such records are excluded by verifier eligibility before the
policy predicate is evaluated.

### Theorem 3: Current dependency closure

Every currently established claim has currently available declared
dependencies.

**Proof sketch.** Availability of every declared dependency is a conjunct in
the definition of admissibility, which is itself a conjunct in current
establishment.

### Theorem 4: Declared-dependency retraction completeness

After RETRACT(x), every object reachable from \(x\) through reverse declared
dependency edges is not live.

**Proof sketch.** RETRACT computes the reverse transitive closure by graph
traversal and appends one retraction event for each member. No transition
reactivates an identifier.

This theorem is deliberately relative to declared dependencies. It says
nothing about omitted real-world dependencies.

### Theorem 5: Authorization safety

If all effects pass through the kernel's token-checking execution boundary,
then no executed effect/resource pair lies outside the task contract's
permission set.

**Proof sketch.** AUTHORIZE-ACTION issues a token only for exact members of the
permission set. The execution-boundary assumption excludes alternative effect
paths.

### Theorem 6: Ledger mutation detection

Assuming collision resistance of the selected hash and an authentic trusted
head, modification, deletion, insertion, or reordering of a historical event
causes ledger verification to fail.

The hash chain supplies tamper evidence, not source truth, non-repudiation, or
durable external timestamping.

## 8. Explicit non-theorems

The formal core does not establish:

- semantic correctness of the task contract;
- truth or completeness of observations;
- soundness of a registered verifier;
- completeness of the dependency graph;
- behavioral fidelity of capability metadata;
- safety of effects outside the sandbox;
- independence merely from distinct labels;
- generalization of a promoted capability;
- efficiency relative to an ordinary agent; or
- decreasing dependence on a proposal model.

Any document that derives these claims from the six kernel theorems exceeds the
formal result.

## 9. Implementation correspondence

- src/jitc/model.py defines immutable contracts, claims, evidence, policies,
  permissions, and envelopes.
- src/jitc/ledger.py implements the append-only hash-linked ledger.
- src/jitc/runtime.py implements declarations, admission, current validity,
  retraction, exact permission checks, and emission.
- schemas/ecir.schema.json and src/jitc/ecir.py define and strictly load the
  first task-contract representation.
- src/jitc/repository.py binds authorization to exact command content, hashes
  an explicit regular-file environment manifest before and after execution,
  and turns a no-shell repository execution into a verifier result.
- tests/test_runtime.py exercises individual invariants and boundary cases.
- tests/test_state_space.py explores bounded event sequences and checks the
  invariants after every accepted or rejected transition.

The Python implementation is a reference executable semantics, not a hardened
security boundary. Repository path confinement, command binding, and paired
environment measurements do not provide an atomic filesystem snapshot or
syscall, network, credential, or resource isolation.
