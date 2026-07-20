# Adversarial Review Framework: Just-in-Time Cognition and the Epistemic Runtime

> Role: fictional senior professor and hostile-but-constructive program-committee reviewer. This document does not claim MIT affiliation. Its purpose is to make the proposed work defensible, not agreeable.

## Executive verdict

**Current recommendation: reject as a research paper; strongly encourage a narrower resubmission backed by a working system.**

The proposal contains one potentially important research program inside several claims that are currently too broad. The potentially important program is:

> Compile an explicit task contract into a transient, provenance-carrying computation that acquires evidence, instantiates local assumptions, invokes capabilities, and discharges machine-checkable obligations; then compile successful traces into reusable, guarded capabilities.

That is worth building. The following stronger claims are not presently defensible:

- that the system has few or no priors;
- that assumptions can be created purely “just in time” without inherited bias;
- that the system makes pretraining irrelevant;
- that a sparse proof hypergraph solves the combinatorics of open-ended cognition;
- that verified artifacts imply truth in an open world; or
- that the result is a fundamentally new kind of intelligence rather than a synthesis of blackboard systems, planning, program synthesis, truth maintenance, provenance, query optimization, incremental computation, and LLM tool use.

The idea becomes publishable if the authors stop selling absence of priors and instead measure **where priors reside, how much they cost, how replaceable they are, and whether task-specific competence can migrate from opaque pretrained weights into inspectable, independently verified artifacts**.

That reframing is not cosmetic. It turns a philosophical assertion into an empirical systems hypothesis.

## The strongest defensible thesis

The paper should make this claim, or something close to it:

> For tasks with partially mechanizable verification, an epistemic runtime can improve reliability and amortized efficiency by representing goals, assumptions, evidence dependencies, authority, and acceptance conditions explicitly; compiling only the task-relevant subgraph; and promoting successful traces into guarded capabilities. Over a task stream, this organization may reduce dependence on any one pretrained proposal model without claiming prior-free learning or universal verification.

This thesis is narrower than “replace pretraining,” but it has measurable content:

1. explicit contracts should reduce unsupported outputs;
2. typed provenance should permit exact invalidation and incremental recomputation;
3. guarded capabilities should create positive transfer without silently expanding their domain of validity;
4. task-local compilation should reduce sequential work relative to unconstrained agent loops; and
5. proposer substitution or degradation should become less harmful as the verified capability library matures.

If the system cannot demonstrate those five effects, there is no paper here beyond an architecture essay.

## Fatal objections unless repaired

### 1. “No assumptions” is impossible; the proposal merely moves them

A finite learner cannot treat all hypotheses, observations, actions, and representations equally. It must choose:

- a contract syntax and semantics;
- a representation of states, claims, evidence, and actions;
- a capability vocabulary;
- a retrieval index and ranking policy;
- a proposal distribution;
- an experiment-selection criterion;
- a verifier family;
- a cost model;
- an authority model; and
- stopping and acceptance rules.

Every item is an inductive bias. The [No Free Lunch result](https://doi.org/10.1109/4235.585893) is not a slogan that forbids useful general systems, but it does force the authors to name the non-uniform problem distribution on which their choices should work. “Information is one click away” does not solve this: knowing what to query, which source to trust, what observation distinguishes two hypotheses, and when to stop are precisely the intelligence problem.

**Required repair:** replace “assumption-free” with **prior relocation and late binding**. Define a prior inventory and report the amount of task-relevant structure present in each component. A web corpus, a package manager, a theorem prover, a test suite, an API schema, and a pretrained retriever are inherited structure, not neutral reality.

### 2. “Pretraining irrelevance” is currently accounting fraud

If an LLM proposes branches, translates goals into obligations, writes queries, chooses tools, or interprets results, the runtime still depends on pretraining. If the system retrieves documentation written by people, invokes libraries produced over decades, or searches an indexed internet, it is consuming civilization’s prior training through a different interface.

Deleting one model’s weights while retaining its generated skills, traces, indexes, embeddings, tool descriptions, and curated benchmark infrastructure does not demonstrate independence. It demonstrates distillation or externalization.

**Required repair:** distinguish at least four claims:

1. **Model substitutability:** one pretrained proposer can be replaced by another with bounded loss.
2. **Model amortization:** proposer calls per solved task decline as verified capabilities accumulate.
3. **Weight independence:** a task can be solved without a large pretrained generative model at runtime.
4. **Cultural independence:** competence can be reconstructed without pretrained models *or* human-produced external knowledge.

The first two may be attainable. The third may be attainable in bounded domains. The fourth is implausible and unnecessary.

### 3. The compiler analogy hides the hard part: task semantics

A conventional compiler receives a program whose semantics are defined. “Make checkout work,” “diagnose the bug,” “design a safe bridge,” and “tell the truth” do not arrive with operational semantics. Translating a human goal into a contract is itself an abductive, normative, and frequently political act.

If the contract is wrong, perfectly discharging it produces the wrong outcome. If the same model writes both the obligations and the proof narrative, the system is circular. Permission tokens do not cure semantic misalignment; they only gate named operations.

**Required repair:** make contract construction part of the object of study. Identify which fields are supplied by a human, synthesized by a model, inferred from the environment, or derived from policy. Measure specification error separately from planning and execution error. Require independent contract review for high-impact tasks.

### 4. Open-world “verification” is not verification

Tests prove only that a program passed those tests in that environment. Sources provide testimony, not truth. A bridge simulator omits some physical facts. A web page may be stale or adversarial. Even a formal proof establishes a theorem relative to an axiom set, formal model, and trusted computing base.

The slogan “a claim cannot cross the output boundary until its obligations are discharged” either:

- limits the system to formally decidable, closed-world claims; or
- mislabels defeasible evidence as proof; or
- prevents useful uncertain answers from crossing the boundary.

**Required repair:** create an assurance lattice rather than a Boolean verified/unverified bit. For example:

```text
speculative < source-supported < independently corroborated
            < experimentally reproduced < mechanically checked
            < formally proved relative to declared assumptions
```

Every output must state its assurance class, open assumptions, provenance, verifier identity, freshness, and known blind spots. “Discharged” must mean different things for different obligation types.

### 5. A proof hypergraph organizes search; it does not make search easy

The proposal assumes the task-relevant graph can be generated sparsely. Determining relevance is often as hard as solving the task. Candidate generation, representation invention, causal hypothesis formation, and verifier construction remain outside the graph or are delegated to an LLM.

Once those pieces are included, familiar lower bounds return:

- general planning is computationally hard;
- expressive HTN planning can become undecidable, as classical complexity analysis already showed ([Erol, Hendler, and Nau](https://www.cs.umd.edu/~nau/papers/erol1996complexity.pdf));
- synthesis is combinatorial and depends heavily on a restricted DSL and ranking prior;
- adaptive information acquisition cannot in general be parallelized past sequential dependencies; and
- some worlds remain observationally indistinguishable under the available budget.

Sparse matrices, semirings, factor graphs, meet-in-the-middle search, canonicalization, partial evaluation, and incremental recomputation are excellent implementation techniques. None is a general antidote to hypothesis-space explosion.

**Required repair:** state the tractable fragment. Specify bounded graph width, capability arity, obligation language, verifier decidability, and environmental observability assumptions. Prove something inside that fragment and benchmark graceful failure outside it.

### 6. The proposal generator is the hidden mind

If `PROPOSE` is implemented by a frontier LLM, then the LLM supplies semantic grounding, analogy, hypothesis formation, query generation, program synthesis, and relevance judgment. The runtime may improve discipline around this mind, but it has not replaced it.

The decisive experiment is not “can a smaller model run the same trace?” Of course it can. It is whether a weaker or non-neural proposer can handle *novel missing transformations* once benchmark leakage, reusable templates, and strong retrievers are controlled.

**Required repair:** treat `PROPOSE` as an explicit oracle with a metered information budget. Report:

- proposer identity and training status;
- calls, tokens, latency, and monetary/energy cost;
- information supplied in tool descriptions and examples;
- fraction of accepted obligations whose verifier is also model-based;
- fraction of successful traces containing a genuinely novel edge; and
- performance under proposer substitution, degradation, and removal.

### 7. Semantic grounding has been deferred to tools and humans

Symbols such as `failure`, `cause`, `evidence`, `safe`, and `success` do not ground themselves. Their meaning comes from sensors, tool contracts, social conventions, and human interpretation. In software, a failing test offers unusually crisp grounding. In medicine, policy, science, or physical action, it often does not.

**Required repair:** begin with software maintenance and explicitly call it a high-observability, partially closed-world domain. Do not infer general cognition from success there. A second domain should differ along observability and verifier quality, not merely surface vocabulary.

### 8. The skill registry can become a second opaque model

A growing library of guarded capabilities faces:

- overly narrow guards, causing no reuse;
- overly broad guards, causing unsafe transfer;
- interacting preconditions and version drift;
- dependency conflicts;
- duplicated or semantically equivalent skills;
- adversarial or poisoned traces;
- verifier obsolescence;
- index and retrieval errors; and
- combinatorial composition failure.

If retrieval and composition require a large learned ranker, the proposal has rebuilt a model around a database. If skills are aggressively distilled, provenance may be lost. If every trace is retained, storage and validation cost grow without bound.

**Required repair:** define capability identity, subsumption, equivalence, versioning, revocation, composition soundness, and garbage collection. Measure registry growth against coverage, retrieval latency, transfer benefit, and false reuse. Include poisoning and stale-dependency tests.

### 9. “Verified memoization” fails under distribution shift

A cached proof is reusable only if its assumptions and environmental invariants still hold. In an open system, checking those preconditions can cost as much as resolving the task, and unmodeled conditions can invalidate the result.

**Required repair:** every capability needs a machine-checkable guard plus an explicit residual-risk statement. The runtime must support negative transfer detection, revocation, and exact dependent invalidation. Evaluate temporal shift, dependency upgrades, altered tool semantics, and adversarially near-matching contexts.

### 10. Verification after action can be too late

For external actions, failure may be irreversible: money transferred, data disclosed, machine damaged, person harmed. Sandbox success does not ensure real-world validity because the sandbox is itself a model. A nominal permission does not establish that action arguments satisfy the user’s intent.

**Required repair:** distinguish epistemic assurance from action safety. Require pre-action simulation where meaningful, least authority, transactionality, dry runs, impact bounds, independent approval for irreversible actions, and compensating actions. Prohibit the initial research system from autonomous high-impact action.

### 11. Novelty is not established

The paper currently recombines known ideas:

- Blackboard architectures already coordinate heterogeneous knowledge sources around shared partial solutions ([Nii, 1986](https://doi.org/10.1609/aimag.v7i3.550)).
- HTN and classical planning already compile goals through operators and preconditions.
- Truth-maintenance and provenance systems track assumptions and derived beliefs.
- Build systems and incremental databases invalidate dependent results and recompute selectively.
- Query optimizers choose low-cost plans for declarative goals; System R did this in 1979 ([Selinger et al.](https://doi.org/10.1145/582095.582099)).
- Program synthesis searches over procedures from specifications; its key dimensions have long been understood as intent, search space, and search technique ([Gulwani](https://www.microsoft.com/en-us/research/publication/dimensions-program-synthesis/)).
- Proof-theoretic synthesis already casts synthesis as verification ([Srivastava, Gulwani, and Foster](https://www.microsoft.com/en-us/research/publication/from-program-verification-program-synthesis/)).
- LLM-agent work already interleaves reasoning, information acquisition, tools, and environment feedback; see [ReAct](https://arxiv.org/abs/2210.03629) and [Toolformer](https://arxiv.org/abs/2302.04761).

“We combine them” can be a systems contribution, but only if the composition produces a demonstrated property no component or obvious baseline provides.

**Required repair:** identify one novel mechanism and one novel empirical phenomenon. The best candidates are:

- an epistemic type system that prevents assumption-contaminated claims from being promoted silently;
- a contract compiler that jointly plans evidence acquisition and capability execution under an assurance lattice;
- trace promotion with guards, adversarial validation, and exact invalidation; or
- a longitudinal demonstration that verified capabilities measurably reduce dependence on the pretrained proposer.

## Salvageable claims

These claims are plausible and interesting if stated precisely:

1. **Task-local epistemic compilation:** a declarative task contract can be lowered into an executable evidence-and-action graph.
2. **Typed uncertainty and provenance:** assumptions, observations, derived claims, actions, and artifacts benefit from distinct types and explicit dependency edges.
3. **Exact invalidation:** provenance permits selective retraction and recomputation when a source, assumption, tool, or environment version changes.
4. **Assurance-aware planning:** plan selection can optimize expected assurance gain per cost rather than merely likelihood of task completion.
5. **Two-speed operation:** common problem structures can follow validated fast paths while novelty invokes slower synthesis.
6. **Guarded trace compilation:** successful trajectories can sometimes become reusable programs with declared preconditions and tests.
7. **Model substitutability:** an architecture can reduce the authority of an LLM by treating it as a proposal oracle whose outputs require independent checks.
8. **Amortized model dependence:** a capability library may reduce strong-model calls over a related task stream.
9. **Hardware-independent efficiency:** sequential decision depth, information acquisitions, proposal-oracle calls, and invalidated work are useful measures apart from raw FLOPs.

Do not call any of these “general intelligence” until demonstrated across substantively different domains.

## Formal definitions the paper must supply

### Task contract

Define a task instance as:

\[
T = (G, E_0, \mathcal{A}, \mathcal{C}, \mathcal{V}, \Pi, B, U)
\]

where:

- \(G\): goal predicates or desired properties;
- \(E_0\): initial evidence with provenance and timestamps;
- \(\mathcal{A}\): admissible assumptions and scoping rules;
- \(\mathcal{C}\): capability schemas with preconditions, effects, costs, and versions;
- \(\mathcal{V}\): verifier schemas and their trusted computing bases;
- \(\Pi\): permissions and impact constraints;
- \(B\): budgets over time, queries, oracle calls, compute, money, and risk;
- \(U\): output obligations, including acceptable assurance levels.

State which parts are user-authored, generated, retrieved, or fixed by platform policy.

### Epistemic objects

At minimum, distinguish:

- **Observation:** externally obtained datum with acquisition operation and provenance.
- **Assumption:** locally scoped proposition adopted without sufficient evidence.
- **Claim:** proposition with a derivation and assurance label.
- **Obligation:** predicate and required assurance threshold that an output must meet.
- **Action:** environment transition requiring authority and an impact estimate.
- **Artifact:** persistent output plus its derivation, dependencies, verifier results, and validity interval.
- **Capability:** a partial transformation from typed inputs to typed outputs with guards, side effects, cost distribution, and validation history.

### Soundness and completeness boundaries

Do not claim global soundness. Prove a conditional theorem such as:

> If capability contracts and verifiers are sound relative to model \(M\), all derivation edges are recorded, and no effect occurs outside declared interfaces, then every emitted mechanically checked claim is derivable in \(M\) from its declared observations and assumptions.

Then enumerate exactly why the theorem may fail in deployment.

### Prior inventory

Define the inherited information budget:

\[
P = L(R) + L(C_0) + L(V) + L(I) + L(M) + L(D)
\]

where \(L\) is an agreed description or storage measure for runtime \(R\), initial capabilities \(C_0\), verifiers \(V\), indexes/retrievers \(I\), proposal model \(M\), and demonstrations/configuration \(D\). A perfect Kolmogorov measure is impossible; an operational accounting is still better than pretending the quantity is zero.

Report external knowledge accessed separately by bytes, sources, and provenance class.

### Dependence and amortization metrics

Define, before seeing results:

- **Oracle-call rate:** strong-proposer calls per accepted task.
- **Sequential epistemic depth:** longest dependency chain containing an external observation or proposal decision.
- **Evidence efficiency:** obligation-weighted assurance gain per external acquisition cost.
- **Invalidated work ratio:** cost of work later retracted divided by total cost.
- **Registry utility:** successful reuse benefit minus lookup, validation, and maintenance cost.
- **Transfer precision:** fraction of capability reuses that remain valid under independent evaluation.
- **Model substitution loss:** change in task utility when replacing the proposer under a fixed budget.
- **Amortization slope:** change in proposer dependence over a chronological task stream.
- **Contract error rate:** failures caused by an incorrect or incomplete contract rather than planning or execution.
- **Verifier escape rate:** outputs accepted by the internal verifier but rejected by an independent oracle or expert audit.

### Cold reconstruction levels

The phrase “cold reconstruction” must specify what remains:

- **L0:** remove answer cache only.
- **L1:** remove task traces; retain skill registry and strong proposer.
- **L2:** remove learned skills; retain strong proposer, tools, and external information.
- **L3:** remove strong proposer; retain verified skills, retriever, tools, and external information.
- **L4:** remove strong proposer and learned skills; retain runtime, hand-built primitives, and external information.
- **L5:** retain only runtime and raw sensors/data, with no curated index or human knowledge artifacts.

Success at L3 would be useful. L4 would be remarkable in a bounded domain. L5 is not a sensible near-term requirement.

## Required system architecture for an honest prototype

The minimum credible system is not a new language parser. Use a typed JSON or data-model representation first.

1. **Contract store:** goals, obligations, assurance levels, budgets, permissions.
2. **Append-only evidence ledger:** observations, sources, timestamps, tool versions, hashes.
3. **Dependency hypergraph:** claims, assumptions, obligations, capabilities, and derivations.
4. **Capability registry:** typed signatures, guards, side effects, validators, cost distributions, versions, revocations.
5. **Planner/query optimizer:** backward chaining from obligations and forward propagation from available evidence.
6. **Proposal-oracle interface:** interchangeable LLM, symbolic, enumerative, and retrieval-based proposers with metering.
7. **Verifier interface:** deterministic tests, differential checks, formal tools, independent model critics, and human review, labeled by assurance strength.
8. **Authority layer:** read/write/action scopes, dry-run semantics, impact bounds, and approval hooks.
9. **Trace promoter:** converts successful traces into candidate capabilities, then tests them against held-out and adversarial cases before registry admission.
10. **Invalidation engine:** retracts claims and artifacts when assumptions, sources, dependencies, or environments change.

The runtime should be able to explain not “why I believe this” in prose, but exactly which versioned dependencies caused the artifact to be admitted.

## Evaluation program

### Phase 1: verifiable software diagnosis

Use a domain where claims can be tested without pretending tests are universal truth.

Construct a chronological suite of repository tasks containing:

- reproducible defects with known inducing changes;
- underspecified reports requiring information acquisition;
- misleading symptoms and plausible distractors;
- flaky tests;
- stale documentation;
- dependency upgrades;
- security-sensitive operations;
- near-duplicate bugs where naive skill reuse is wrong; and
- genuinely novel bug mechanisms.

For each task, retain a hidden adjudication package: root cause, minimal causal intervention, relevant environment conditions, and independent regression tests. Avoid using only public benchmarks likely present in proposer training.

Primary outcomes:

- independently adjudicated task success;
- verifier escape rate;
- strong-proposer calls and tokens;
- external tool calls;
- sequential epistemic depth;
- wall-clock time and dollar cost;
- unsafe or unauthorized action attempts;
- contract construction errors;
- capability reuse precision; and
- longitudinal change in all metrics.

### Phase 2: shifted software environment

Repeat after changing language version, dependency APIs, test runner behavior, repository conventions, and tool output formats. This tests exact invalidation and negative transfer rather than benchmark memorization.

### Phase 3: a domain with weaker verification

Choose one domain where evidence is defeasible but harms are bounded, such as literature-backed technical forecasting on events with later resolution. The purpose is to test the assurance lattice and calibration, not autonomous action.

Do not jump directly from software to medicine, finance, critical infrastructure, or claims of universal intelligence.

## Baselines

All learned baselines must receive the same base model, context budget, tools, documentation corpus, permissions, and total cost budget unless the comparison explicitly studies one factor.

At minimum:

1. direct tool-using LLM;
2. ReAct-style agent;
3. plan-and-execute agent with reflection/retry;
4. agent plus ordinary vector memory and cached solutions;
5. deterministic workflow/HTN planner with hand-authored operators;
6. blackboard-style system with the same capability sources;
7. program-synthesis or CEGIS baseline for tasks expressible in the chosen DSL;
8. provenance-aware Datalog or rule engine;
9. incremental build/query engine for invalidation and replanning microbenchmarks; and
10. oracle upper bounds using ground-truth contracts or perfect capability retrieval.

The purpose of classical baselines is not nostalgia. If an LLM wrapper cannot beat a 1980s-style blackboard with modern tools, the architectural rhetoric is unsupported.

## Ablations

The paper needs all of the following:

- remove typed distinctions among assumption, observation, and claim;
- remove provenance and exact invalidation;
- replace assurance lattice with a Boolean verifier;
- remove backward compilation from obligations;
- remove forward reachability propagation;
- remove cost-aware information acquisition;
- remove parallel hypothesis branches;
- remove trace promotion;
- promote traces without adversarial held-out validation;
- remove capability guards;
- remove registry garbage collection and revocation;
- replace the strong proposer with a weaker model;
- replace the proposer with retrieval plus enumerative search;
- let the proposer also act as verifier, then require an independent verifier;
- use static versus shifting environments;
- compare cold versus warmed registry chronologically; and
- randomly permute or poison a small fraction of tool descriptions and stored skills.

Report interactions, not only one-factor averages. Typed provenance may matter only when shift occurs; trace promotion may help only with repeated structure; parallel branches may worsen cost under weak verifiers.

## Experiments that specifically test the speed thesis

Raw hardware-normalized latency is insufficient. The proposed advantage is algorithmic.

1. **Dependency-depth experiment:** synthetically vary the number of inherently sequential observations while holding total graph size fixed. Demonstrate that the runtime approaches the critical-path lower bound.
2. **Factorization experiment:** vary conditional independence structure while holding the naive Cartesian hypothesis count fixed. Measure explored states and proposal calls.
3. **Invalidation experiment:** change one source at different graph centralities and measure recomputed work versus full rerun.
4. **Information-gain experiment:** supply experiments with known partition structure and compare query policies against random, greedy entropy, and oracle selection.
5. **Fast-path experiment:** repeat task families with controlled structural similarity; measure when compiled capabilities beat fresh inference after including guard-checking and retrieval overhead.
6. **Novelty experiment:** introduce tasks requiring a capability absent from the registry and report cache-miss cost honestly.
7. **Break-even analysis:** estimate the recurrence rate required for trace promotion and validation to amortize.

Any claim of “lightning fast” should be replaced by a Pareto curve over success, assurance, sequential depth, external queries, proposer tokens, and total cost.

## Pre-registered kill criteria

The authors should commit in advance to conditions under which the central hypothesis is considered unsupported.

1. Under matched model, tools, and budget, the complete runtime does not improve independently adjudicated success or verifier escape rate over a strong ReAct/plan-and-execute baseline.
2. Apparent efficiency vanishes when contract-generation, retrieval, validation, and registry-maintenance costs are included.
3. Strong-proposer calls per accepted task do not decline over a chronological related-task stream, or decline only because tasks repeat verbatim.
4. Model substitution loss remains constant or worsens as the registry grows.
5. More than half of accepted high-level obligations are adjudicated solely by the same model family that proposed them.
6. Capability transfer precision falls below the direct-agent baseline under near-match distribution shift.
7. Registry size grows roughly linearly with tasks while marginal reuse benefit approaches zero.
8. Trace promotion causes net negative utility after validation, lookup, invalidation, and poisoning defense are counted.
9. The system cannot distinguish contract error from execution error in postmortem audit.
10. “Cold reconstruction” succeeds only when benchmark-specific templates, leaked traces, or semantically equivalent pretrained services remain available.
11. The system’s only demonstrated domain is one with a near-perfect executable verifier, yet the paper retains open-world or general-intelligence claims.
12. Claimed speedups come primarily from more parallel hardware, a larger hidden context, or a stronger proposer rather than reduced search or information requirements.

These criteria are intentionally harsh. A research program that cannot be wrong is not a research program.

## What would make this publishable

### Minimum publishable systems paper

Title it conservatively, for example:

> **Epistemic Contracts: Assurance-Aware Compilation for Verifiable Software Agents**

Contributions:

1. a formal contract and epistemic object model;
2. a working runtime with provenance, assurance-aware planning, exact invalidation, and guarded trace promotion;
3. a controlled evaluation against both modern LLM agents and classical planning/provenance baselines;
4. evidence of reduced verifier escapes and positive longitudinal transfer under matched budgets; and
5. candid negative results on open-world verification and model removal.

### Strong paper

Add:

- a conditional soundness theorem;
- a query-selection or planning result for a clearly specified tractable fragment;
- proposer-substitution experiments showing declining dependence on the original model;
- a distribution-shift study demonstrating revocation and exact invalidation; and
- a second domain with weaker verification and calibrated assurance labels.

### Field-defining result

Demonstrate all of the following without benchmark leakage:

1. a long chronological stream of novel tasks;
2. growing competence with sublinear registry or maintenance cost;
3. decreasing strong-model dependence under fixed total utility;
4. successful reconstruction at cold level L3 or L4 in a nontrivial domain;
5. high transfer precision under adversarial near-match shift;
6. independent verification not dominated by the proposal model; and
7. an empirical scaling law relating inherited prior budget, information acquisition, synthesis cost, and achieved competence.

That would justify talking about an alternative route to foundation-model-centric AI. It still would not justify “no priors,” but it might justify “pretraining is no longer the primary container of competence.”

## Recommended paper structure

1. **Problem:** opaque pretrained competence is stale, difficult to invalidate, weakly provenance-aware, and hard to audit.
2. **Scope:** tasks with heterogeneous but explicit assurance mechanisms; software as the first domain.
3. **Thesis:** relocate some competence into late-bound evidence acquisition, typed derivations, and verified reusable capabilities.
4. **Related work:** blackboard systems, truth maintenance, planning, synthesis, provenance, incremental computation, query optimization, and LLM agents.
5. **Formalism:** task contract, assurance lattice, capability semantics, derivation graph, conditional soundness.
6. **System:** compiler, ledger, planner, oracle interface, verifier interface, authority layer, promoter, invalidator.
7. **Evaluation:** matched baselines, chronological protocol, shift, ablations, kill criteria.
8. **Limitations:** semantic grounding, verifier incompleteness, inherited cultural structure, open-world uncertainty, irreversible action.
9. **Research agenda:** model amortization and cold reconstruction, not declarations of pretraining’s death.

## Reviewer’s final challenge to the authors

Build the smallest version that can lose.

Do not begin by inventing syntax, naming a new form of intelligence, or claiming a 2126 architecture. Begin with a typed data model and one severe experiment:

> Across a hidden chronological stream of software defects, can explicit epistemic contracts, independent verification, guarded trace promotion, and exact invalidation reduce verifier escapes and strong-model calls relative to a matched tool-using agent, including all overhead and under dependency shift?

If yes, the authors have discovered a mechanism. If the dependence on the pretrained proposer then declines without capability-library collapse, they have discovered the beginning of a different architecture. If not, the “epistemic runtime” is an excellent audit wrapper around an LLM—but it is not yet the machine-native intelligence being claimed.

That distinction is the difference between a compelling vision and a defensible paper.
