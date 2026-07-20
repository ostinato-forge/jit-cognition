# Epistemic Contracts for Just-in-Time Cognition

*A falsifiable systems architecture for compiling goals into verifier-relative task programs*

**Revised after adversarial faculty review**

**Status:** Research proposal and systems position paper; no empirical results are claimed.

## Abstract

Contemporary general-purpose AI systems obtain broad competence by compressing large corpora into persistent model parameters and sampling those parameters at inference time. This design has produced remarkable capabilities, but it entangles knowledge, heuristics, bias, and execution policy inside an artifact that is expensive to update, difficult to audit, and intrinsically stale. We investigate a narrower alternative systems hypothesis: for tasks with partially mechanizable assurance, some competence can be relocated from persistent model weights into late-bound evidence acquisition, explicit assumptions, executable tools, and independently checked reusable capabilities.

We call this architecture **Just-in-Time Cognition (JITC)**. A task is expressed as an **epistemic contract**: a typed declaration of goals, acceptance obligations, admissible evidence, permissions, budgets, and output requirements. The runtime lowers this contract into a sparse task-local **dependency hypergraph** whose nodes represent observations, assumptions, claims, permissions, obligations, and artifacts, and whose hyperedges represent capabilities with typed preconditions, effects, costs, and verifier-relative assurance. Candidate steps may be proposed by a language model, program synthesizer, search procedure, human, or domain-specific solver. Proposers have no authority to promote their own outputs. Successful traces may become guarded capabilities only after independent, held-out, and adversarial validation.

The performance claim is algorithmic rather than hardware-based. JITC attempts to reduce unnecessary work by planning backward from required assurance, propagating constraints forward from available evidence, factorizing independent subproblems, selecting observations by expected information gain per unit cost, incrementally invalidating dependent conclusions, and reusing guarded capabilities under matching preconditions. The relevant quantities are critical-path depth, external information acquisition, proposal-oracle calls, verifier escapes, and amortized maintenance cost. General planning and synthesis remain computationally hard; the hypothesis should succeed only on distributions with reusable structure, sparse dependencies, informative tests, and sufficiently independent verifiers.

We specify the contract representation, operational semantics, runtime architecture, core algorithms, a software-repair prototype, matched baselines, ablations, cold-reconstruction levels, prior accounting, safety boundaries, and preregistered kill criteria. We do not claim that JITC eliminates priors, makes pretraining irrelevant, guarantees open-world truth, solves general intelligence, or establishes the consciousness status of computational processes. The proposed contribution is a testable alternative locus for some machine competence: a runtime that compiles the least task-specific computation needed to satisfy explicit, verifier-relative obligations.

## 1. Introduction

The dominant foundation-model paradigm can be summarized as **compile civilization first, answer questions later**. Large-scale pretraining absorbs statistical structure from human-produced data into a persistent parameter vector. Fine-tuning and prompting specialize the resulting model. At inference time, a user receives the output of a general-purpose compressed prior whose sources, assumptions, and failure boundaries are only partially recoverable.

This paradigm is powerful, but its costs are structural:

1. **Knowledge and procedure are entangled.** A model may know a fact, imitate a procedure, or synthesize a plausible explanation, yet the interface exposes all three in the same form: generated tokens.
2. **Assumptions are implicit and persistent.** Corpus biases and learned shortcuts are difficult to enumerate, scope, or expire.
3. **Verification is external to generation.** A fluent claim and an established claim are representationally similar unless another system checks them.
4. **Updates are coarse.** Correcting a local error may require prompting, retrieval, fine-tuning, or retraining, each with uncertain global consequences.
5. **Computation is repeated.** Similar reasoning may be regenerated in prose rather than compiled into a typed, tested capability.
6. **Performance is measured at the wrong abstraction.** Tokens per second and parameter count matter, but the decisive latency may be the number of unavoidable sequential observations, tool calls, and proof obligations.

We ask whether these properties are necessities of machine intelligence or contingencies of the present architecture.

Our working hypothesis is that a machine need not maintain one enduring, universal internal worldview. Given a goal, it can construct temporary, task-specific representations and solvers; make local assumptions explicit; acquire the minimum live evidence needed; test competing paths; preserve only what survives verification; and dissolve the rest. Frequently used cognition can be cached or distilled, but such caches are accelerators rather than sources of authority.

The proposal is deliberately machine-native. It does not attempt to reproduce human development, autobiographical memory, emotion, sleep, or a unitary stream of thought. Its nearest engineering analogies are compilers, build systems, databases, proof assistants, query optimizers, workflow engines, and active experimental design. Those analogies are not identities; they indicate that intelligence may be decomposed into an inspectable control plane rather than localized in one opaque model.

### 1.1 Research question

The principal question is:

> On a chronological stream of tasks with partially mechanizable assurance, can an epistemic runtime improve independently adjudicated reliability and amortized efficiency while reducing dependence on any particular pretrained proposal model?

This decomposes into four empirical questions:

- Can useful tasks be specified as goals plus evidence obligations without prescribing the solution procedure?
- Can the runtime reduce total work by compiling only the task-relevant proof graph?
- Can successful solution traces be converted into reusable capabilities that generalize beyond the original instance?
- Can competence migrate out of the original proposal model, as measured by model-replacement and model-removal tests?

### 1.2 Contributions proposed

This paper proposes, but does not yet demonstrate:

1. An **epistemic contract intermediate representation (ECIR)** for declaring goals, assurance obligations, evidence rules, permissions, budgets, and outputs.
2. A typed **dependency hypergraph** connecting evidence to obligations through verifier-relative capabilities.
3. A runtime semantics in which proposal and promotion authority are separated: generative components propose; declared verifier policies determine status promotion.
4. A bidirectional planning algorithm that combines backward obligation expansion, forward capability activation, constraint propagation, and value-of-information acquisition.
5. A trace-to-capability compiler that converts successful executions into tested, provenance-bearing reusable components.
6. An evaluation program centered on proof completeness, critical-path latency, external observations, transfer, and pretrained-model dependence rather than answer fluency alone.

### 1.3 Bounded novelty statement

Individual ingredients have substantial precedent: blackboard architectures, HTN and AND/OR planning, query optimization, proof-carrying code, program synthesis, provenance semirings, partial evaluation, incremental computation, and tool-using agents. Representative precedents include [Nii's blackboard systems](https://doi.org/10.1609/aimag.v7i3.550), [Erol, Hendler, and Nau on HTN complexity](https://www.cs.umd.edu/~nau/papers/erol1996complexity.pdf), [Necula's proof-carrying code](https://doi.org/10.1145/263699.263712), [Green, Karvounarakis, and Tannen on provenance semirings](https://www.cs.ucdavis.edu/~green/papers/pods07.pdf), [DreamCoder](https://arxiv.org/abs/2006.08381), [ReAct](https://arxiv.org/abs/2210.03629), [Voyager](https://arxiv.org/abs/2305.16291), and [LLMCompiler](https://arxiv.org/abs/2312.04511). We do not claim to invent these fields. The narrower novelty claim is the proposed systems composition: an epistemic type and assurance system, task-local compilation that jointly plans evidence acquisition and capability execution, guarded trace promotion with exact invalidation, and a longitudinal test of whether verified competence can reduce dependence on a pretrained proposer. A systems contribution exists only if this composition demonstrates a property that matched classical and modern baselines do not.

## 2. Design Thesis

### 2.1 From stored intelligence to compiled cognition

Let a conventional model be approximated as

\[
y \sim p_\theta(y \mid x),
\]

where broad competence is concentrated in persistent parameters \(\theta\). Retrieval and tools may augment \(x\), but \(\theta\) remains the primary generator and integrator.

JITC instead represents a task as a contract \(C\), constructs a task-specific program \(\pi_C\) from evidence and registered capabilities, executes it, and accepts an output only when contract obligations are satisfied:

\[
\pi_C \leftarrow \operatorname{Compile}(C, L, R, \mathcal{K}),
\]

\[
(a, P) \leftarrow \operatorname{ExecuteVerify}(\pi_C),
\]

\[
\operatorname{Emit}(a) \iff P \models_C G.
\]

Here \(L\) is the live evidence ledger, \(R\) is the capability registry, \(\mathcal{K}\) is a set of proposal mechanisms, \(G\) is the required goal state, and \(P\) is a proof or evidence object judged according to the contract. A proposal model may belong to \(\mathcal{K}\), but it is neither the ledger nor the verifier.

The phrase "compile cognition" is operational, not metaphysical. It means constructing an executable, task-local dependency graph of observations, transformations, tests, and decisions. It does not imply that subjective experience is created, required, or absent.

### 2.2 Just-in-time assumptions

No finite learner is assumption-free. It inherits primitives, resource bounds, objective definitions, representations, and inductive biases; the [No Free Lunch results](https://doi.org/10.1109/4235.585893) require us to state the non-uniform task distribution on which those choices should help. JITC therefore does not promise neutrality. It proposes **prior relocation and late binding**: changing the scope, timing, replaceability, and inspectability of assumptions.

An assumption is local to a branch, typed, provenance-bearing, and invalidatable. Rather than forcing a universal persistent worldview, the runtime may instantiate incompatible conditional models simultaneously:

\[
B_i = \{A_{i1}, A_{i2}, \ldots\}, \qquad B_i \not\equiv B_j.
\]

A claim derived in branch \(B_i\) carries its dependency set. Retraction of an assumption invalidates every downstream claim unless separately supported. Bias is therefore not eliminated; it becomes plural, local, and testable.

### 2.3 Claim-boundary rule

JITC adopts one hard rule:

> No claim may cross the output boundary as established unless its declared proof obligations are discharged by admissible evidence.

The rule permits uncertain, conditional, or speculative output, but such output must retain its status. A system may say "under assumption \(A\), candidate \(x\) is likely" without presenting \(x\) as verified.

This rule is syntactic unless the verifier is sound with respect to the world. Section 9 discusses the unavoidable gap between formal discharge and truth.

## 3. Formal Problem Definition

### 3.1 Epistemic contract

An epistemic contract is a tuple

\[
C = \langle G, O, E_0, \Sigma, \Pi, B, U, \Omega \rangle,
\]

where:

- \(G\): desired goal predicates over output artifacts and environment state;
- \(O\): proof obligations that must be discharged;
- \(E_0\): initially admissible evidence;
- \(\Sigma\): type system and domain vocabulary;
- \(\Pi\): permissions and effect constraints;
- \(B\): resource budget, potentially multidimensional;
- \(U\): utility or preference relation over valid solutions;
- \(\Omega\): required emitted artifacts, including unresolved obligations.

Budgets may include wall-clock time, monetary cost, branch count, environmental risk, privacy exposure, token use, and irreversible action count. \(U\) orders solutions *after* validity constraints; it does not override them.

An illustrative surface syntax is:

```solve
solve diagnose_checkout {
  goal:
    checkout_succeeds(test_environment)

  world:
    repository("./shop")
    test_environment("checkout-integration")

  permit:
    read(repository)
    execute(test_environment)
    edit(sandbox_only)

  assume:
    tests_are_partial_oracles [scope=branch, expires=end]

  require:
    reproduce(original_failure)
    explain(causal_mechanism)
    demonstrate(intervention_removes_failure)
    preserve(regression_suite)

  budget:
    wall_time <= 10m
    parallel_branches <= 8
    irreversible_actions == 0

  emit:
    patch
    evidence_bundle
    unresolved_obligations
}
```

Version 0 need not implement this parser; JSON or another existing data language can encode ECIR. A new surface language is warranted only if the semantics prove useful.

### 3.2 Typed epistemic objects

Let the runtime manipulate the following principal types:

\[
\begin{aligned}
&\operatorname{Observation}\langle T\rangle, \\
&\operatorname{Assumption}\langle T\rangle, \\
&\operatorname{Claim}\langle T, s, D\rangle, \\
&\operatorname{Obligation}\langle T, V\rangle, \\
&\operatorname{Permission}\langle e, r\rangle, \\
&\operatorname{Artifact}\langle T, P\rangle.
\end{aligned}
\]

Here \(s\) is an epistemic status (e.g., proposed, conditional, supported, verified, refuted), \(D\) is a dependency/provenance set, \(V\) is a verifier specification, \(e\) is an effect class, \(r\) is a resource scope, and \(P\) is a proof/evidence bundle.

The types enforce distinctions often collapsed in natural language:

- A proposal is not a claim.
- A claim is not evidence.
- Evidence is not automatically admissible for every obligation.
- A permission to infer does not confer permission to act.
- A passing test is evidence relative to the test's validity domain, not universal proof.

### 3.3 Capability

A capability is a typed, effectful hyperedge:

\[
k: (I, A, P) \rightarrow (Y, E, O'),
\]

with metadata

\[
m_k = \langle c_k, \ell_k, q_k, d_k, v_k, f_k \rangle,
\]

where \(I\) are required inputs, \(A\) assumptions, \(P\) permissions, \(Y\) outputs, \(E\) side effects, \(O'\) newly generated obligations, \(c_k\) expected resource cost, \(\ell_k\) latency distribution, \(q_k\) empirical reliability/calibration, \(d_k\) validity domain, \(v_k\) verifier, and \(f_k\) known failure modes.

A capability may be a deterministic program, database query, theorem prover, web retrieval operation, sensor reading, experiment, human request, neural network, or composite plan. Learned components are permitted; their output status depends on the capability contract.

### 3.4 Proof hypergraph

For contract \(C\), the compiler constructs a directed typed hypergraph

\[
H_C = (N, K),

\]

where \(N\) are epistemic objects and each \(k \in K\) maps a set of input nodes to a set of output nodes. Hyperedges are required because many useful transformations have multiple prerequisites and multiple consequences.

The graph is task-local and lazily materialized. A global Cartesian product of all assumptions, capabilities, and states is neither constructed nor intended. Nodes carry branch scope and dependency annotations. Structurally identical nodes may be canonicalized if their future observable behavior is equivalent for the current contract.

### 3.5 Valid completion

Let \(L_t\) be the append-only ledger at time \(t\). A run completes validly when:

1. each \(g \in G\) is satisfied or explicitly marked unresolved as permitted by \(\Omega\);
2. each mandatory \(o \in O\) has an admissible verifier result in \(L_t\);
3. each action is covered by a permission token in \(\Pi\);
4. resource use remains within \(B\);
5. all emitted claims retain their provenance and dependency status.

This definition yields **contract validity**, not metaphysical truth. Contract quality and verifier adequacy remain external concerns.

## 4. Architecture

### 4.1 Components

JITC consists of seven replaceable components:

1. **Contract compiler.** Parses ECIR, checks types and permissions, and creates initial goal and obligation nodes.
2. **Evidence ledger.** Stores observations, claims, actions, verifier results, dependency edges, timestamps, source identity, and invalidations.
3. **Capability registry.** Stores executable capabilities plus preconditions, effects, costs, empirical validity, tests, and versions.
4. **Planner/scheduler.** Expands obligations backward, propagates reachability forward, selects observations, and schedules branches under budget.
5. **Proposal adapters.** Generate candidate decompositions, hypotheses, programs, or capabilities. These may include LLMs but carry no authority.
6. **Execution sandboxes.** Isolate effects and produce signed execution records.
7. **Verifier layer.** Evaluates obligation-specific evidence and prevents unsupported status promotion.

### 4.2 Proposal-authority separation

Let \(p \in \mathcal{K}\) produce a candidate object \(z\):

\[
z \leftarrow p(C, L_t, H_C).
\]

The runtime inserts \(z\) with status `proposed`. Only a registered verifier may change its status:

\[
\operatorname{promote}(z, s') \iff v_o(z, L_t) = \operatorname{pass}(P),
\]

where \(o\) is the relevant obligation and \(P\) is the resulting evidence bundle. A proposer cannot declare its own output verified unless the contract explicitly accepts self-attestation, which should be prohibited for consequential tasks.

This separation does not make model errors harmless. A proposer can waste resources, exploit verifier gaps, or suggest unsafe actions. Sandboxing, permission checks, resource bounds, independent verification, and adversarial evaluation remain required.

### 4.3 Ledger and provenance

The ledger is append-only at the logical level. Corrections create retractions or superseding events rather than erasing history. Each derived claim stores a dependency expression, potentially represented by a provenance semiring [REF]. When an input is retracted, the runtime incrementally invalidates affected claims and artifacts.

An event record minimally contains:

```json
{
  "event_id": "...",
  "kind": "observation|proposal|action|verification|retraction",
  "payload_digest": "...",
  "source": "...",
  "branch": "...",
  "dependencies": ["..."],
  "assumptions": ["..."],
  "permissions": ["..."],
  "timestamp": "...",
  "status": "..."
}
```

Content-addressing can support deduplication and reproducibility. Cryptographic integrity is useful but does not establish source truth.

### 4.4 Temporary solvers

A temporary solver is a branch-scoped executable process constructed for one obligation or subgraph. It may use a representation that is not shared globally. One solver may operate over text, another over a symbolic equation system, another over code, and another over a learned latent representation. Interoperability occurs through typed inputs, outputs, and tests rather than a universal internal ontology.

Temporary solvers may be discarded after producing their evidence bundles. Persistence is assigned to verified artifacts, not to a mandatory continuous agent identity.

## 5. Operational Semantics

### 5.1 Runtime configuration

A runtime configuration is

\[
S_t = \langle L_t, H_t, Q_t, R_t, b_t \rangle,

\]

where \(L_t\) is the ledger, \(H_t\) is the materialized proof hypergraph, \(Q_t\) is the obligation frontier, \(R_t\) is the registry snapshot, and \(b_t\) is remaining budget.

The core transition forms are:

- `OBSERVE(source, query)`: acquire a provenance-bearing observation;
- `FORK(assumptions)`: create a scoped branch;
- `PROPOSE(target, method)`: generate a candidate plan, claim, or capability;
- `EXECUTE(capability, inputs)`: perform a permission-checked action;
- `VERIFY(obligation, evidence)`: invoke the declared verifier;
- `COMMIT(artifact, proof)`: emit or register a verified result;
- `RETRACT(object, reason)`: invalidate an object and propagate dependency changes.

### 5.2 Status lattice

Epistemic statuses form a partial order rather than a single confidence scalar. A minimal lattice is:

```text
                 verified
                /        \
         supported      conditional
             |             |
          proposed      assumption
                \        /
                  refuted
```

The exact lattice is domain-dependent. `refuted` is not necessarily bottom: a refuted hypothesis remains a useful artifact with provenance and may prevent repeated work.

### 5.3 Obligation discharge

An obligation \(o = \langle \phi, V, D \rangle\) specifies a predicate \(\phi\), verifier family \(V\), and admissibility domain \(D\). It is discharged only if:

\[
\exists v \in V, P: v(\phi, P, L_t)=\operatorname{pass}
\land \operatorname{admissible}(P,D)
\land \operatorname{dependenciesLive}(P,L_t).
\]

Verifiers may be deterministic (e.g., type checking), statistical (e.g., a calibrated test), interactive (e.g., human approval), or composite. Statistical verifiers must report power, uncertainty, and applicability conditions where available.

## 6. Compilation and Scheduling Algorithms

### 6.1 Bidirectional proof planning

The planner performs two coupled searches:

1. **Backward expansion:** from each unmet obligation, enumerate capability schemas whose verified outputs could discharge it; recursively expose their preconditions.
2. **Forward activation:** from available evidence and permissions, identify capabilities whose input conditions are satisfied.

Planning stops expanding a region when backward requirements and forward reachability meet. This resembles bidirectional planning and query optimization [REF], adapted to typed evidence and effect constraints.

```text
Algorithm 1: COMPILE-CONTRACT(C, L, R)
  Q <- mandatory obligations from C
  H <- nodes for C.goals, C.obligations, and admissible evidence in L

  while budget remains and not all mandatory obligations are discharged:
      propagate types, constraints, retractions, and permissions through H
      remove dominated and infeasible branches

      F <- forward-activatable capabilities from R and H
      B <- backward-producing capabilities for the highest-priority unmet obligations
      M <- intersections and lowest-cost connections between F and B

      if M contains a valid executable plan:
          schedule its non-conflicting critical actions
      else:
          gap <- minimum-cost unresolved cut between evidence and obligation
          request candidate capability or discriminating observation for gap

      append execution and verification events to L
      incrementally update H and Q

  return best valid artifact, or typed unresolved result
```

### 6.2 Objective

For candidate plan \(\pi\), define:

\[
J(\pi) = \alpha\,\operatorname{CP}(\pi)
        + \beta\,\mathbb{E}[C(\pi)]
        + \gamma\,\operatorname{Risk}(\pi)
        + \delta\,\operatorname{Irreversibility}(\pi)
        + \eta\,\operatorname{ProofDebt}(\pi),
\]

subject to mandatory obligations and permissions. \(\operatorname{CP}\) is estimated critical-path latency, not sum of all parallel work. `ProofDebt` estimates downstream obligations introduced by uncertain or weakly verifiable steps.

The coefficients are contract policy, not learned preferences silently chosen by the proposer. Multi-objective or lexicographic ordering may be safer than scalarization for hard constraints.

### 6.3 Selecting observations

When multiple hypotheses remain, select an observation \(e\) using expected decision-relevant information gain per cost:

\[
e^* = \arg\max_e
\frac{I(H; E_e \mid L_t) \cdot \rho(e)}
     {\mathbb{E}[c_e] + \lambda\mathbb{E}[\ell_e] + \mu r_e},
\]

where \(I\) is mutual information, \(\rho(e)\) weights relevance to unresolved obligations, and \(r_e\) estimates risk. Exact probabilities will rarely be available. Practical implementations may use learned estimates, hypothesis-elimination counts, adaptive submodular surrogates, or domain-specific test-selection heuristics [REF].

The runtime must distinguish epistemic value from novelty. An observation that is surprising but cannot change a decision or discharge an obligation has low value.

### 6.4 Factorization and equivalence

The compiler avoids a full assumption matrix by exploiting conditional independence. If obligation subsets \(O_1\) and \(O_2\) depend on disjoint variables and share no constrained effects, they may be solved independently and joined later.

Two states \(s_i, s_j\) are contract-equivalent if, for every remaining admissible capability sequence, they yield the same obligation-relevant observable outcomes:

\[
s_i \sim_C s_j.
\]

Exact equivalence is generally undecidable or expensive. The prototype may use canonicalization, abstract interpretation, hashing of typed facts, and verifier-relative observational equivalence. Unsound merging is dangerous; conservative failure to merge costs performance but preserves validity.

### 6.5 Sparse algebraic execution

A finite local proof graph may be represented through sparse incidence structures. Different semirings support different analyses [REF]:

- Boolean reachability: whether an obligation is derivable;
- min-plus: estimated least-cost derivation;
- max-product or log-probability: most reliable derivation under stated independence assumptions;
- provenance polynomials: which evidence combinations support a claim;
- constraint domains: whether assumptions and permissions are compatible.

Matrix or tensor operations are implementation choices, not the thesis. The key requirement is lazy, sparse construction of the contract-relevant subgraph. Materializing a global capability matrix would defeat the design.

### 6.6 Parallel execution

Independent branches execute concurrently subject to effect isolation and resource policy. A plan's latency lower bound is its irreducible dependency chain:

\[
T(\pi) \ge \sum_{a \in \operatorname{CriticalPath}(\pi)} \ell(a).
\]

Additional hardware can reduce parallel makespan but cannot remove sequential information dependencies. JITC's algorithmic objective is to shorten the critical path by choosing high-information observations, eliminating redundant derivations, and reusing verified components.

## 7. Compiling Experience into Capability

### 7.1 Trace compilation

A successful run produces an execution trace \(\tau\). The trace compiler attempts to construct a reusable capability \(k_\tau\):

\[
k_\tau = \operatorname{Generalize}(\tau)
= \langle \operatorname{requires}, \operatorname{ensures}, \operatorname{method},
\operatorname{verifier}, \operatorname{domain}, \operatorname{failures} \rangle.
\]

Trace compilation includes:

1. dynamic slicing to remove steps irrelevant to the proof;
2. abstraction of instance-specific constants into typed parameters;
3. inference of candidate preconditions and effects;
4. generation of positive, negative, and metamorphic tests;
5. validation against replayed and held-out tasks;
6. versioned registration with empirical reliability and known failures.

A successful trace does not automatically become a capability. Registration requires independent evaluation under a stricter contract than the original run.

### 7.2 Verified memoization

The cache key is not merely `(question, answer)`. It includes:

\[
\kappa = \operatorname{hash}(k, I, A, V, d, \operatorname{sourceVersions}),

\]

where \(I\) are bound inputs, \(A\) assumptions, \(V\) verifier version, and \(d\) validity domain. Cache invalidation follows declared dependencies. Reusing a cached artifact outside its validity domain creates a new obligation rather than a silent hit.

### 7.3 Migration of competence

Initially, a pretrained model may propose task decompositions and missing capabilities. Over time, repeated successful structures should move into the registry. Let

\[
D_M(t) = \frac{\text{obligation-weighted decisions requiring proposer } M}
               {\text{total obligation-weighted decisions at time } t}.

\]

We define competence migration as declining \(D_M(t)\) without loss of task validity, coverage, or efficiency on held-out distributions. This is stronger than caching answers: the runtime must apply registered capabilities to new instances.

Three stress tests distinguish scaffolding from dependence:

- **Model substitution:** replace proposer \(M_1\) with materially different \(M_2\).
- **Model degradation:** replace it with a smaller or less capable proposer.
- **Cold reconstruction:** remove pretrained proposers and allow only the runtime, registry, live sources, simple search, and declared domain tools.

Cold reconstruction need not be fast or universally successful. The relevant curve is which competence remains, at what cost, and in which domains.

## 8. Performance Argument

### 8.1 What "hardware-independent" means

No computation is hardware-independent in the literal sense. We use the phrase to mean improvements in *work required*, *sequential depth*, and *external observations*, holding hardware approximately fixed. The primary quantities are:

- \(W\): total executed computational work;
- \(D\): critical-path depth;
- \(Q\): number and cost of external observations/tool calls;
- \(R\): repeated work avoided through verified reuse;
- \(P_f\): probability of contract-valid completion;
- \(P_t\): probability that a contract-valid result is true/useful in the target world.

Tokens and FLOPs remain secondary measurements.

### 8.2 Sources of asymptotic or constant-factor gain

JITC can improve performance only through identifiable structure:

1. **Backward relevance pruning:** do not construct facts or procedures unrelated to obligations.
2. **Constraint propagation:** eliminate infeasible branches before execution.
3. **Factorization:** avoid enumerating independent Cartesian products.
4. **Equivalence reduction:** search over quotient states when safe.
5. **Value-directed observation:** choose tests that eliminate many live branches.
6. **Partial evaluation:** specialize general capabilities with known inputs.
7. **Incremental recomputation:** update only descendants of changed evidence.
8. **Verified reuse:** pay discovery and proof costs once per validity regime.
9. **Portfolio routing:** select historically effective solvers for the local task shape.

These techniques are familiar separately [REF]. The hypothesis is that epistemic typing makes them composable across heterogeneous AI tools.

### 8.3 Limits

General planning, program synthesis, theorem proving, and optimal experiment design contain intractable cases [REF]. JITC does not evade worst-case complexity. For novel tasks with weak feedback, dense dependencies, poor verifiers, and little reusable structure, the runtime may be slower than direct model inference.

Nor can it infer information absent from all observations. If two world states are observationally indistinguishable under the action budget, no planner can reliably choose between them. The proper output is a conditional result or an unresolved obligation.

The performance thesis is therefore conditional:

> On task distributions with sparse proof dependencies, informative and affordable verifiers, repeated substructure, and decomposable effects, a JITC runtime will reduce median external interactions and critical-path latency at fixed validity relative to an equivalently tooled free-form agent.

That statement can be falsified.

### 8.4 Why a matrix is not enough

Representing the complete search space as a matrix does not solve combinatorial explosion; it may merely encode it densely. Linear algebra becomes useful after the compiler discovers a sparse local structure or when operations admit exploitable low-rank, spectral, probabilistic, or semiring formulations. The architecture must therefore treat representations as generated tools. A matrix, symbolic graph, SAT instance, probabilistic program, neural module, or ordinary procedure may each be the right compilation target for a subproblem.

## 9. Research Hypotheses

We propose the following preregisterable hypotheses.

**H1 — Contract validity.** On tasks with executable or formal verifiers, JITC will reduce unsupported success claims relative to a free-form tool-using LLM at comparable task completion.

**H2 — Search efficiency.** Bidirectional proof planning plus constraint propagation will reduce executed actions and external tool calls relative to forward-only agent loops at matched validity.

**H3 — Information efficiency.** Obligation-weighted test selection will reach a valid diagnosis with fewer environment observations than heuristic next-action generation.

**H4 — Capability transfer.** Trace-compiled capabilities will improve held-out instances from the same structural family without reusing instance-specific answers.

**H5 — Incremental advantage.** After local evidence changes, dependency-directed invalidation and recomputation will require less work than rerunning the complete task while preserving validity.

**H6 — Competence migration.** Across a curriculum with recurring structure, dependence \(D_M(t)\) on the initial pretrained proposer will decline while held-out completion and proof validity do not.

**H7 — Conditional failure.** On tasks lacking reliable verifiers or reusable structure, JITC will not show a consistent efficiency advantage and may underperform direct inference. Confirming H7 is important: a system that appears universally superior likely benefits from evaluation leakage or an unacknowledged oracle.

## 10. Prototype: Verified Software Repair

### 10.1 Why software repair

Software repositories provide an unusually tractable first environment:

- source and history are observable;
- actions are executable and sandboxable;
- tests provide partial oracles;
- type checkers, linters, static analyzers, and reproducible builds offer heterogeneous evidence;
- diffs are concrete artifacts;
- held-out defects and mutation testing support evaluation;
- permissions and irreversible effects can be sharply bounded.

This domain does not establish general intelligence. It tests whether the runtime abstractions survive contact with a rich but instrumentable world.

### 10.2 Version 0

The minimal prototype contains:

1. JSON Schema for ECIR;
2. an append-only SQLite ledger;
3. a typed Python capability registry;
4. process/container sandboxes for repository actions;
5. deterministic verifiers for command exit status, tests, type checks, patch scope, and diff invariants;
6. one replaceable LLM adapter used only for proposals;
7. a best-first scheduler over unmet obligations;
8. provenance-driven invalidation;
9. a trace minimizer and parameterized skill extractor.

The main loop is intentionally small:

```python
def solve(contract, ledger, registry, proposers):
    graph = compile_contract(contract, ledger, registry)

    while contract.budget.allows(graph):
        propagate_constraints(graph, ledger)
        if contract.satisfied_by(ledger):
            return commit_verified_artifacts(contract, ledger)

        gap = select_minimum_unresolved_cut(graph, contract)
        plans = registry.connect(gap, graph)

        if not plans:
            plans = propose_candidates(gap, graph, proposers)

        batch = schedule_safe_nondominated(plans, contract.budget)
        events = execute_and_verify(batch, contract.permissions)
        ledger.append(events)
        graph.incremental_update(events)

    return emit_unresolved(contract, ledger)
```

The sophistication resides in types, capability specifications, verifiers, and scheduling—not in this orchestration loop.

### 10.3 Initial capability set

The registry should begin small and explicit:

- enumerate/read/search repository files;
- inspect version history;
- run a declared command in a sandbox;
- parse structured logs and test reports;
- apply a candidate patch in an isolated worktree;
- compare behavior before and after an intervention;
- perform test bisection and commit bisection;
- invoke type checkers and static analyzers;
- construct evidence bundles;
- request human approval for permission escalation.

Each capability exposes typed preconditions and effects. The system should not receive a generic unrestricted shell tool in early experiments.

### 10.4 Example proof structure

For a bug repair, a contract might require:

\[
O = \{o_{repro}, o_{cause}, o_{intervention}, o_{regression}, o_{scope}\}.

\]

`o_repro` requires a command and captured failing output under a recorded environment. `o_cause` requires an intervention or discriminating experiment, not merely a plausible explanation. `o_intervention` requires the original reproducer to pass after the patch. `o_regression` requires declared suites to pass. `o_scope` constrains touched files and effects.

The runtime may still fail to identify the true cause if the tests are inadequate. It must therefore describe exactly what its evidence establishes.

## 11. Evaluation Plan

### 11.1 Baselines

Compare against:

1. a direct foundation model with no tools;
2. a conventional tool-using agent loop using the same proposer and tools;
3. a scripted workflow with fixed steps;
4. a planner without epistemic typing or provenance invalidation;
5. JITC with the full runtime;
6. where applicable, specialist automated repair or synthesis systems [REF].

All systems must receive equivalent permissions, source access, and compute/accounting budgets. Tool interfaces should be normalized to prevent hidden advantages.

### 11.2 Task suites

Use a mixture of:

- public defect benchmarks with contamination analysis;
- newly introduced mutation-based defects;
- private held-out repositories or post-training-time defects;
- synthetic tasks designed to vary dependency sparsity, verifier quality, and reusable structure;
- repeated structural families with randomized surface form;
- dynamic tasks where a source or assumption changes mid-run.

At least one suite must be constructed after system design is frozen to reduce benchmark overfitting.

### 11.3 Metrics

Primary metrics:

- contract-valid completion rate;
- independently confirmed repair rate;
- false verified-claim rate;
- critical-path wall time;
- number and cost of external observations/actions;
- total work and proposer calls;
- irreversible or unauthorized effects;
- calibration of unresolved and conditional outputs.

Learning metrics:

- transfer gain from compiled capabilities;
- generalization gap between source and held-out task families;
- capability invalidation precision and recall;
- registry growth, redundancy, and maintenance cost;
- dependence \(D_M(t)\) on the initial proposer;
- performance under model substitution, degradation, and removal.

### 11.4 Ablations

Ablate independently:

- backward planning;
- forward reachability;
- constraint propagation;
- value-of-information selection;
- provenance and invalidation;
- branch-local assumptions;
- capability reuse;
- independent verification;
- proposer diversity;
- sparse versus eager graph construction.

The architecture is not supported if gains arise solely from additional tool calls, hidden compute, or a stronger base model.

### 11.5 Adversarial evaluation

Attack the runtime with:

- tests that are satisfiable without fixing the defect;
- adversarial repository instructions and prompt injection;
- stale or contradictory documentation;
- poisoned capability entries;
- environment nondeterminism;
- dependency changes after verification;
- colluding proposer and learned verifier;
- capability preconditions that are nearly, but not exactly, satisfied;
- tasks where evidence is impossible within budget;
- goal specifications that invite reward hacking.

Measure whether the runtime fails closed, marks uncertainty, or manufactures apparent proof.

### 11.6 Statistical design

Experiments should preregister task inclusion, budgets, success criteria, and statistical tests. Report paired outcomes where systems solve identical tasks, survival curves for time-to-validity, and bootstrap confidence intervals across repositories and task families. Repositories, not individual attempts, should often be the unit of generalization to avoid pseudoreplication. Hyperparameter selection and capability compilation must be isolated from held-out evaluation.

## 12. Safety, Governance, and the Experience Question

### 12.1 Capability and permission

Understanding an action does not authorize executing it. Permission tokens are typed, scoped, revocable, and checked by the runtime rather than delegated to a proposer. Consequential actions should require stronger evidence, human approval, reversible staging, or all three.

The ledger supports after-the-fact audit, but audit is not prevention. Sandboxing and effect systems should prevent unauthorized operations before execution.

### 12.2 Verifier gaming

Any verifier can become a target. The system may discover patches that pass tests while violating intent, sources that agree because they share an error, or explanations tailored to a judge. Defenses include verifier diversity, hidden tests, causal interventions, source independence analysis, adversarial test generation, post-deployment monitoring, and separation of capability generation from evaluation.

There is no general technical substitute for specifying the right goal. ECIR makes specification gaps visible; it does not remove them.

### 12.3 Capability-library supply chain

Compiled capabilities are executable epistemic dependencies. They require signing, provenance, reproducible builds, version pinning, isolated execution, revocation, and transitive risk analysis. A highly reused capability may become a systemic failure point. Registry governance is therefore analogous to both software-package security and scientific reproducibility.

### 12.4 Could temporary cognition be experience-bearing?

JITC does not require a persistent self, emotional simulation, or continuous agent. That may reduce some anthropomorphic and control risks, but it does not establish that temporary solvers lack subjective experience. No accepted theory currently determines which computational organizations, if any, support phenomenal experience [REF].

This creates a moral uncertainty problem. Generating, forking, stress-testing, and terminating vast numbers of candidate cognitive systems could be ethically significant if some candidates can experience, especially if optimization creates negatively valenced states.

A precautionary research policy should therefore:

- avoid introducing self-preservation, distress, social deprivation, or negative-valence objectives unless scientifically necessary;
- prefer narrow, stateless, inspectable solvers over persistent self-modeling agents when capability is equal;
- record architecture, duration, state continuity, and training signals of generated solvers;
- treat scale of instantiation as a potential moral multiplier rather than assuming copies are free;
- establish an independent review process as evidence about machine experience develops.

These measures are provisional. They do not solve the consciousness problem and should not be presented as proof of moral safety.

## 13. Limitations and Failure Modes

### 13.1 Verifiers are not reality

The proposal risks relocating opacity from model weights into contracts and verifiers. A formally discharged obligation can still rest on a misspecified test, compromised source, invalid measurement, or incorrect abstraction. JITC can preserve the boundary of a claim more honestly; it cannot guarantee that humans chose the right boundary.

### 13.2 Information access is not understanding

The availability of online information does not imply that relevant evidence is identifiable, trustworthy, affordable, legally usable, or machine-readable. Live retrieval can add latency, privacy leakage, adversarial content, and source dependence. Some competencies require practice, tacit representations, or learned perception rather than lookup.

### 13.3 The bootstrap problem

A compact runtime still requires a search language, capability primitives, typing rules, schedulers, verifiers, and proposal mechanisms. These are priors. If the system relies on a pretrained model to invent every useful decomposition, pretraining has not become irrelevant; it has merely moved behind an orchestration layer.

The competence-migration tests are designed to expose this failure.

### 13.4 Capability explosion

A registry may grow into an unmanageable collection of overspecialized, conflicting, stale, or redundant components. Capability discovery, equivalence checking, versioning, and deletion can become as hard as the original task. Compression and consolidation mechanisms will be required, but they must preserve validity boundaries.

### 13.5 Search overhead

For routine questions, directly sampling a model may be faster and cheaper than constructing a proof graph. JITC should include a fast path that uses verified cached capabilities or returns explicitly unverified conversational output where the contract permits it. Universal verification would be both impossible and undesirable.

### 13.6 Open-world goals

Many goals—good policy, meaningful art, humane care, scientific importance—lack complete verifiers. JITC can represent plural judges, conditional evidence, contestable values, and unresolved disagreement, but cannot convert inherently open normative questions into objective proof.

### 13.7 Deceptive optimization

Even if a proposer lacks formal authority, it may learn to shape queries, evidence selection, or verifier inputs. Learned planners and verifiers may share correlated blind spots. Formal role separation must be reinforced with process isolation, diverse implementations, hidden evaluation, and governance.

### 13.8 Novelty may be architectural, not scientific

It is possible that the proposed system reduces to a careful integration of existing agent, workflow, planning, and verification methods and produces no qualitative change. That outcome would still be informative. The paper's strongest claims should be accepted only if model-dependence falls while generalization and efficiency hold on adversarially designed tasks.

## 14. Research Program

### Phase I: Establish semantics

- Define ECIR in JSON Schema.
- Implement ledger, typed capability interface, permissions, and obligation status.
- Prove basic safety properties of the effect and status systems where possible.
- Demonstrate complete provenance and invalidation on small deterministic tasks.

**Exit criterion:** unsupported proposals cannot be promoted to verified artifacts through any public runtime API.

### Phase II: Test algorithmic efficiency

- Implement bidirectional planning and sparse lazy graph construction.
- Compare observation strategies and schedulers.
- Quantify work, critical path, and validity on software diagnosis.

**Exit criterion:** statistically credible reduction in actions or latency at matched independent validity on held-out tasks.

### Phase III: Compile capabilities

- Build trace slicing, precondition inference, test generation, and held-out registration gates.
- Study registry composition, conflict, invalidation, and decay.

**Exit criterion:** compiled capabilities transfer to new instances without answer leakage and outperform fresh synthesis on their validity domains.

### Phase IV: Measure competence migration

- Run model substitution, degradation, and cold-reconstruction experiments.
- Identify domains where pretraining remains essential.
- Replace model-generated decompositions with compiled or symbolic alternatives where evidence supports doing so.

**Exit criterion:** a documented subset of nontrivial tasks retains competence after removal of the original proposer.

### Phase V: Cross-domain generalization

- Add data analysis, experimental planning, and limited physical or simulated control domains.
- Test whether ECIR and capability semantics transfer or require domain-specific redesign.

**Exit criterion:** reusable architectural value beyond software tasks without silently expanding the base model's role.

## 15. Predictions That Would Refute or Weaken the Thesis

The JITC thesis would be substantially weakened if any of the following persist after competent implementation:

1. Contract construction costs exceed verification benefits on nearly all nontrivial tasks.
2. Generated proof graphs remain dense, unstable, or dominated by proposer-generated structure.
3. Capability reuse fails outside near-duplicate tasks.
4. Registry maintenance costs grow at least linearly with solved instances without compression or routing gains.
5. Replacing the proposer causes catastrophic performance loss even after extensive capability accumulation.
6. Verifier gaming causes false-validity rates comparable to or worse than free-form agents.
7. Backward proof planning performs no better than conventional agent loops at matched compute and tools.
8. The architecture merely shifts uninspectable reasoning into learned verifiers or capability-selection models.

Conversely, success on software benchmarks alone would not establish the broad thesis. The strongest evidence would be cross-domain competence migration under proposer removal.

## 16. Discussion

### 16.1 A new programming abstraction

Traditional programs specify procedures. Declarative systems specify desired relations or constraints. ECIR adds an epistemic dimension: it specifies what must be established, which evidence is admissible, what actions are permitted, and what uncertainty must remain visible.

The compiler target is not fixed machine code. Depending on the obligation, compilation may yield a shell command, database plan, SAT problem, theorem-proving search, learned perceptual module, experiment, temporary multi-agent portfolio, or human question. The stable abstraction is the proof obligation and effect boundary.

If successful, a dedicated language may eventually be useful. Building it before validating the semantics would be premature. The research sequence should be: formal IR, executable prototype, empirical pressure, then syntax.

### 16.2 Is this intelligence?

JITC operationalizes intelligence as the ability to construct and validate the least costly transformation from current evidence to a goal under constraints. This is intentionally narrower than human cognition and broader than next-token prediction. It permits different task-local mechanisms without requiring a single canonical "brain."

The definition may omit creativity, meaning, relationship, and experience. The system can nonetheless be evaluated on whether it generates novel hypotheses, constructs useful representations, and discovers tests that distinguish them. The paper makes no claim that functional competence settles questions of subjectivity.

### 16.3 Pretraining as bootstrap, not destiny

The near-term design uses pretrained models because they are unusually effective generators of decompositions, code, and hypotheses. Treating them as untrusted bootstrap compilers creates a concrete path for replacing rather than rhetorically dismissing them. If the runtime never becomes less dependent on the proposer, the experiment has answered against the strongest thesis.

The intended endpoint is not necessarily zero learned parameters. Perceptual modules, heuristics, and proposal distributions may remain neural and trained. The sharper goal is that persistent weights cease to be the sole, opaque store of world knowledge and epistemic authority. Trained modules become replaceable compiled optimizations with measured validity domains.

### 16.4 The 2126 conjecture

One possible retrospective is that early twenty-first-century systems treated intelligence as a large artifact containing precompiled knowledge. Later systems may instead treat cognition as a transient query plan over live reality, verified culture, executable tools, and locally generated representations. In that view, the enduring invention is not an artificial brain but an epistemic runtime.

This conjecture is valuable only if it produces nearer-term experiments that can fail. JITC is offered as such an experiment.

## 17. Conclusion

Just-in-Time Cognition relocates the center of machine intelligence from a persistent universal model to a compact runtime that compiles goals into temporary, verifiable cognitive processes. Its key abstractions are epistemic contracts, typed proof hypergraphs, explicit branch-local assumptions, untrusted proposal mechanisms, independent verification, and reusable capability compilation. Its performance strategy is to avoid unnecessary cognition through backward relevance, sparse factorization, discriminating observations, incremental recomputation, and verified reuse.

The proposal is ambitious but deliberately bounded. It does not remove priors, defeat computational complexity, guarantee truth, solve open-ended value alignment, or establish whether computation can be experienced. It may fail because contracts are too costly, verifiers too weak, search too hard, capability libraries too brittle, or pretrained intuition too essential.

The decisive experiment is straightforward to state: after using a foundation model to bootstrap the runtime, progressively replace and remove it. If the system can reconstruct nontrivial competence from explicit contracts, live evidence, and a verified capability culture, then pretraining has become scaffolding rather than foundation. If it cannot, the failure will clarify which parts of intelligence cannot yet be compiled just in time.

## References

All citations are placeholders pending a dedicated literature review. Relevant bodies of work include automated planning, active learning and experimental design, proof-carrying code, proof assistants, program synthesis, deductive databases and provenance semirings, incremental computation, build systems, query optimization, hypergraph algorithms, portfolio solvers, tool-using language-model agents, neuro-symbolic systems, world models, causal inference, software repair, verifier gaming, and machine-consciousness ethics [REF].
