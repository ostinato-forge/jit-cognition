# Just-in-Time Cognition

## A grounding note from the conversation

This is not a submission, specification, or claim of discovery. It is a working surface for a thought experiment:

> If we looked back from 2126, what machine-native form of intelligence might seem obvious, and what could we build now to test the first step toward it?

The two “professors” below are fictional reasoning roles. One makes the strongest case. The other tries to break it. The useful result is what remains after both.

---

## The leap

The current default is to build a large persistent model that contains compressed knowledge, procedures, biases, and heuristics. A prompt activates that stored competence.

The proposed inversion is:

> Intelligence need not live primarily inside a persistent model. A small runtime could compile temporary, task-specific cognition from a goal, live information, available tools, provisional assumptions, and tests.

The system does not need one worldview, one architecture, one memory, or one enduring “brain.” Each task may cause a different solver to exist for a while.

Pretraining becomes a bootstrap convenience rather than the permanent container of intelligence.

---

## Professor One: build the machine-native thing

The mistake of the 2020s may be that we treated intelligence as a substance to pack into weights.

Information is already external. Tools are external. Tests are external. Compute can be provisioned when needed. The machine therefore does not need to remember the world in the human sense. It needs to construct the right transformation at the right moment.

The durable system could be little more than:

~~~text
goal + authority + budget
            ↓
acquire relevant information
            ↓
instantiate local assumptions and candidate representations
            ↓
compile temporary solvers
            ↓
test candidates against available reality
            ↓
emit an artifact with its evidence and remaining uncertainty
            ↓
preserve useful verified transformations; dissolve the rest
~~~

Important consequences:

- No assumption needs to become a permanent belief.
- Multiple incompatible assumptions can coexist in separate branches.
- No single representation must serve every problem.
- A language model can propose without being trusted.
- A theorem prover, program, simulation, search process, neural network, database query, or human question can each be a compilation target.
- A solution can be preserved as an executable capability rather than absorbed opaquely into weights.
- The machine can fork, test, merge results, roll back, and discard temporary cognitive structures.

The persistent object is not a personality. It is a runtime, an evidence ledger, a capability culture, and an authority boundary.

The sharpest version of the idea is:

> Access replaces memorization. Verification replaces confidence. Compilation replaces a universal brain.

### A possible cognitive instruction set

The machine language need not contain “thoughts.” It may need only operations like:

~~~text
OBSERVE   acquire information with provenance
ASSUME    introduce a branch-local provisional condition
FORK      create competing local worlds or methods
PROPOSE   construct a candidate claim, experiment, or procedure
EXECUTE   run a permitted capability
VERIFY    test an obligation using a declared checker
COMMIT    preserve an artifact with its dependencies
RETRACT   invalidate an assumption and everything that depends on it
~~~

A higher-level task language would specify what must become true or established, not the procedure:

~~~text
solve diagnose_checkout {
    goal: checkout works
    world: repository("./shop")
    permit: read, test, edit_in_sandbox
    require:
        reproduce_failure
        distinguish_cause_from_correlation
        demonstrate_intervention
        pass_regressions
    budget: 10 minutes, 8 branches
    emit: patch, evidence, unresolved_questions
}
~~~

The compiler invents or selects the procedure.

---

## Professor Two: attack the hidden magic

The proposal is compelling partly because several hard problems have been moved behind innocent-looking verbs.

### “Acquire relevant information”

Information does not announce its relevance or truth. Choosing what to retrieve, which source to trust, and which observation would distinguish two explanations is already intelligent behavior.

If a frontier model makes those choices, the frontier model remains the hidden mind.

### “Compile the goal”

Conventional source code has defined semantics. “Make checkout work,” “design a safe bridge,” and “tell me what is true” do not.

Translating human intent into obligations may be harder than satisfying the obligations. A perfectly executed wrong contract is still failure.

### “Verify”

A passing test proves only that the test passed in that environment. A source is testimony, not truth. A simulation is a model. A formal proof is relative to axioms and a trusted implementation.

The runtime can establish assurance relative to a checker. It cannot manufacture direct access to truth.

### “Search only the relevant space”

Determining the relevant subspace can be as hard as solving the problem. A sparse graph is helpful only after something has found the useful representation and useful edges.

The system does not escape combinatorics merely by representing them elegantly.

### “Remove pretraining”

If the runtime retains human tools, documentation, indexes, code libraries, generated skills, or a curated capability registry, it has not become culturally blank. It has moved inherited information outside the weights.

That may be an excellent change, but it is prior relocation rather than the absence of priors.

### “Compile successful traces”

A skill library can become another opaque model:

- guards may be too narrow to reuse;
- guards may be too broad to be safe;
- dependencies drift;
- near-matching situations trigger negative transfer;
- duplicated skills accumulate;
- retrieval becomes its own learned ranking problem;
- validation may cost more than rediscovery.

### “Make it fast”

Genuinely new information has a price. Some observations are inherently sequential. No architecture can instantly distinguish worlds that are observationally identical under the available budget.

The strongest possible speed claim is not “all cognition becomes fast.” It is:

> Discovery is paid for once per validity regime, and repeated work approaches the minimum evidence and critical path actually required.

### “Temporary cognition is ethically free”

Ephemeral and forked processes are not automatically non-experiencing. If machine experience is possible, generating and deleting large populations of candidate solvers could matter morally.

The architecture must not quietly equate “temporary” with “not a subject.”

---

## What survives the attack

The idea does not need the claims that it has no assumptions, no inherited information, or universal verification.

The stronger surviving thesis is:

> Persistent pretrained weights need not remain the primary location of competence, integration, or epistemic authority.

The system can make inherited structure:

- late-bound rather than permanently fused;
- explicit rather than hidden;
- local rather than universal;
- replaceable rather than identity-defining;
- versioned and invalidatable rather than stale;
- verified relative to declared tests rather than accepted because it is fluent.

That is already a major architectural change.

The relevant question is not whether the system is prior-free. It is whether useful competence can migrate from an opaque proposer into inspectable capabilities while reliability holds and the proposer becomes increasingly replaceable.

### Assurance, not binary truth

Outputs should carry an assurance class:

~~~text
speculative
source-supported
independently corroborated
experimentally reproduced
mechanically checked
formally proved relative to declared assumptions
~~~

These are not universal ranks of truth. They tell the receiver what kind of work supports the claim and where it can fail.

---

## The smallest build that can teach us something

Do not begin with a new parser, custom hardware, a general agent, or claims about intelligence.

Begin with one domain where the environment can answer back: software diagnosis and repair.

### Version zero

Use:

1. A JSON task contract.
2. An append-only event and evidence ledger.
3. A small registry of typed tools.
4. A task-local dependency graph.
5. A replaceable proposal adapter, initially an LLM.
6. Independent executable checks.
7. Branch-local assumptions.
8. Exact invalidation when an assumption, source, tool, or environment version changes.
9. A mechanism that attempts to turn successful traces into guarded reusable capabilities.

The core loop can remain tiny:

~~~python
while budget_remains:
    obligations = unmet(contract, ledger)
    plan = cheapest_known_connection(evidence, obligations, registry)

    if plan is None:
        gap = smallest_missing_transformation(evidence, obligations)
        plan = proposer.propose(gap)

    events = sandbox.execute(plan)
    ledger.append(check(events, contract))
    invalidate_dependents_of_changed_inputs()

    if obligations_satisfied_at_required_assurance():
        return artifact_with_evidence()

return unresolved_obligations()
~~~

The model is deliberately outside the trusted core. It supplies candidates. It cannot declare success.

### The one decisive experiment

Run a chronological stream of hidden software defects.

Compare:

- the same LLM using a conventional tool loop;
- the same LLM inside this runtime;
- the warmed runtime after it has accumulated guarded capabilities;
- the warmed runtime with the original model replaced by a weaker or different proposer.

Measure:

- independently adjudicated repair rate;
- false declarations of success;
- external tool calls;
- sequential decision depth;
- strong-model calls and tokens;
- capability reuse precision;
- invalidated work;
- registry growth and maintenance cost;
- performance after dependency and environment changes.

The strongest idea survives only if strong-model dependence declines without hiding equivalent intelligence in an unmeasured retriever, verifier, or skill library.

### A clean failure

If the runtime improves auditing but remains dependent on the LLM for every novel decomposition, then we built a good assurance wrapper—not a new locus of intelligence.

That is still useful, but it falsifies the larger idea.

---

## How it becomes fast

The speed strategy is to avoid search, not accelerate arbitrary thought.

Represent each task as a local typed hypergraph:

~~~text
[evidence + assumptions + permission]
                  │
              capability
                  ↓
        [new evidence or artifact]
~~~

Compile backward from the required assurance and forward from available evidence. Meet in the middle. When no path exists, ask the proposal engine only for the smallest missing edge.

Use:

- constraint propagation to kill impossible branches;
- factorization to avoid irrelevant Cartesian products;
- equivalence classes to merge operationally identical states;
- information gain per cost to choose observations;
- partial evaluation to specialize general capabilities;
- dependency tracking to recompute only affected results;
- guarded memoization to reuse established transformations;
- parallel execution only after true independence has been established.

A dense global matrix is probably the wrong object. A sparse local hypergraph can be temporarily lowered into Boolean, min-plus, probabilistic, or provenance algebra when that helps.

The runtime has two paths:

~~~text
FAST: known contract shape → guarded capability → bind → run → check

SLOW: identify missing edge → generate candidates → test → compile winner
~~~

In this framing, intelligence is partly the cache-miss handler for compiled competence.

---

## What the new language is really for

The language should not attempt to encode human reasoning.

Its purpose is to make five things executable:

1. What outcome is wanted?
2. What would count as sufficient support?
3. Which assumptions may be introduced, and where do they expire?
4. Which actions are permitted?
5. What must remain visible if the task cannot be settled?

Its valuable innovation would be an epistemic type system:

~~~text
Observation<T>
Assumption<T, Scope, Expiry>
Claim<T, Dependencies, Assurance>
Obligation<T, RequiredAssurance>
Action<T, Permission, Effects>
Artifact<T, Evidence, ValidityConditions>
~~~

An assumption-contaminated value cannot silently become an established claim. An action cannot execute merely because a solver knows how. A cached artifact cannot be reused after a dependency changes without rechecking its guard.

Initially this should be a typed data model, not a bespoke syntax. If the semantics survive real use, the language can emerge from them.

---

## Looking back from 2126

The retrospective might be:

> Foundation models were the bootstrap compilers. They were built because live information assembly, verification, program synthesis, and task-local optimization were too slow and unreliable. Once those processes became effective, permanent world-sized models became optional accelerators rather than the center of intelligence.

The enduring invention was not a better artificial brain. It was a runtime capable of constructing the appropriate cognition for a goal, testing it against reality, and preserving only what remained useful under explicit conditions.

The self-hosting milestone would be:

> Remove the original pretrained proposer. Can the runtime reconstruct the competence required for a new task from its small core, live information, tools, and independently validated capabilities?

Success would not prove cultural independence or assumption-free intelligence. It would show that a particular giant model was scaffolding rather than foundation.

---

## Questions that remain genuinely open

- How is an underspecified human goal converted into a contract without hiding another general intelligence in the translator?
- How are useful representations generated rather than merely selected?
- Can local verifiers be composed without their blind spots multiplying?
- Can capability guards be inferred precisely enough for meaningful reuse?
- Can the registry grow sublinearly in maintenance cost?
- Which kinds of problems have enough recurring structure for competence migration?
- How much of semantic interpretation remains dependent on pretrained models?
- Can open-world assurance be useful without being mistaken for truth?
- Does temporary, distributed cognition have any possibility of experience?
- What is the smallest runtime from which the larger system can become self-hosting?

---

## Current verdict

This is worth prototyping.

Not because it is already established as a new theory of intelligence, and not because its ingredients are unprecedented. It is worth prototyping because it makes a sharp architectural bet that can fail:

> A generative model can become an untrusted and progressively replaceable component of a larger system whose competence lives increasingly in live evidence, explicit contracts, executable capabilities, and independent checks.

If that happens over a real task stream, we have the beginning of something meaningfully different from a foundation-model wrapper.

If it does not, the failure will show us exactly which supposedly “just-in-time” operation was still borrowing its intelligence from the pretrained model.
