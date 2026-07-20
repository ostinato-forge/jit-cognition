# Research Charter

## 1. The claim

The defensible JITC thesis is:

> For task distributions with partially mechanizable assurance, repeated
> structure, and enforceable effect boundaries, an epistemic runtime can turn
> explicit task contracts into evidence-directed executions, admit outputs only
> under declared policies, invalidate conclusions when recorded support fails,
> and promote validated traces into guarded capabilities. Over a chronological
> task stream, this may reduce false acceptance and dependence on any particular
> proposal model after all maintenance costs are counted.

The phrase "compile cognition" is operational. It means lowering an explicit
contract into a task-local execution and evidence plan. It does not assert that
the runtime creates consciousness, eliminates learned priors, or discovers the
semantics of an ambiguous human request for free.

## 2. The architectural wager

The project bets on relocating authority, not eliminating models.

Foundation models are useful proposal engines because they amortize enormous
amounts of search and cultural knowledge. JITC does not deny this. It asks
whether the model must also remain:

- the persistent store of every reusable procedure;
- the arbiter of whether its own output is established;
- the owner of action permissions;
- the only mechanism for adapting after dependencies change; and
- the irreplaceable integrator for familiar task families.

The expected near-term architecture is hybrid:

~~~text
ambiguous human request
        |
        v
intent elaboration and review          untrusted or human-authorized
        |
        v
epistemic contract (ECIR)              explicit boundary
        |
        v
compiler and policy checker            trusted core
        |
        v
planner and proposal adapters          untrusted search and synthesis
        |
        v
sandboxed capability execution         enforced effects
        |
        v
verifier-specific evidence records     declared assurance
        |
        v
artifact admission or unresolved result
        |
        v
candidate capability promotion         held-out and adversarial gate
~~~

## 3. Compilation is not synthesis

The earlier formulation used "compile" for too many operations. The refined
architecture separates three stages:

1. **Elaboration** translates an underspecified request into a reviewable
   contract. It may require a model, domain template, policy, or human decision.
   It is not in the trusted compiler.
2. **Compilation** performs deterministic or otherwise checked lowering from
   ECIR into obligations, permitted effects, and an executable plan skeleton.
   Compiler passes must preserve the contract's declared semantics.
3. **Synthesis** proposes missing decompositions, experiments, programs, or
   capabilities. Synthesis is explicitly untrusted and cannot admit its output.

This split prevents task semantics and representation invention from hiding
inside an innocent compiler verb.

## 4. Epistemic state has independent axes

JITC does not use one universal confidence or status lattice. The following
properties are represented separately:

- **Kind:** observation, assumption, claim, obligation, action, or artifact.
- **Lifecycle:** proposed, admitted, rejected, retracted, or superseded.
- **Scope:** branch, environment, version set, time interval, and task.
- **Support:** typed evidence records and their dependencies.
- **Admission:** a policy-specific predicate over currently live support.
- **Uncertainty:** calibrated quantities when meaningful for a verifier.

"Verified" is therefore not an intrinsic label. It is shorthand for a relation:

> claim C was accepted by policy P using verifier V and evidence E, under
> assumptions A, environment W, dependency versions D, at time t.

Different assurance mechanisms are not placed in a universal total order. A
formal proof relative to a weak model is not automatically stronger than a
well-powered experiment for a claim about the physical world.

## 5. Trusted computing base

The minimal trusted computing base (TCB) contains:

- the ECIR parser and type checker;
- admission-policy evaluation;
- permission and effect enforcement;
- the append-only event ledger and dependency index;
- retraction/invalidation propagation;
- sandbox and execution adapters;
- verifier implementations explicitly trusted by a contract; and
- the human or policy roots that authorize the contract.

The following are outside the TCB:

- language models and other proposers;
- natural-language explanations;
- retrieved skill descriptions;
- candidate plans;
- automatic guard inference;
- automatically generated tests until independently admitted; and
- capability implementations beyond what the sandbox can enforce.

A small TCB is not a claim that the whole system is small. External knowledge,
retrievers, tools, verifiers, capability libraries, and human infrastructure
must all be counted in the inherited information and operating cost.

## 6. What can be proved

Under explicit assumptions about the TCB, the project can prove conditional
properties such as:

1. No public transition admits a claim without a currently satisfied admission
   policy.
2. A proposer cannot self-attest when authority separation is required.
3. Every currently established claim has live recorded dependencies.
4. Retracting an object makes every declared transitive dependent unavailable.
5. No action authorization token is issued outside the contract's exact
   permission set.
6. Mutating a recorded ledger event breaks hash-chain integrity.

These are useful but deliberately narrow. They establish properties of the
runtime's bookkeeping and control plane, not truth in the external world.

## 7. What remains empirical

The following cannot be obtained from the kernel proof:

- that a human request was elaborated into the right contract;
- that recorded dependencies include every real dependency;
- that a verifier measures what users intended;
- that a capability's declared behavior matches its actual effects;
- that guard inference generalizes under distribution shift;
- that evidence acquisition is cheaper than direct inference;
- that capability maintenance grows sublinearly; or
- that proposal-model dependence declines on genuinely new tasks.

These are the project's experimental burden.

## 8. Novelty boundary as of July 2026

The field has moved quickly. Closely adjacent work includes:

- SkillOps, which uses typed skill contracts, dependency and compatibility
  graphs, validators, and task-time/library-time maintenance:
  https://arxiv.org/abs/2605.13716
- Recursive Epistemic Engines, which uses typed artifacts, untrusted proposal
  priors, verifier-gated archive admission, experiments, and provenance:
  https://openreview.net/forum?id=6pcrtBtYIi
- Grounded Continuation, which uses explicit claim dependencies and retraction
  in a runtime verifier:
  https://arxiv.org/abs/2605.14175
- proof-carrying untrusted agents for data-pipeline repair:
  https://arxiv.org/abs/2510.09567
- behavioral-integrity verification and skill supply-chain work:
  https://arxiv.org/abs/2605.11770

JITC should not claim novelty from typed skills, graph planning, provenance,
validators, or persistent executable memory individually.

The remaining candidate contribution is the combination of:

1. a task-level epistemic contract that jointly constrains evidence and action;
2. an admission semantics separated from proposal authority;
3. dependency-aware current validity rather than one-time verification;
4. guarded trace promotion with all-in lifecycle accounting; and
5. a longitudinal, intervention-based measurement of whether the original
   proposer becomes causally less important.

The composition is a contribution only if it produces an empirical property
that matched modern and classical baselines do not.

## 9. Product boundary

The near-term product interpretation is an evidence and policy control plane
for agents:

> Every AI-created change carries a machine-readable evidence envelope,
> authority record, validity scope, unresolved obligations, and automatic
> staleness triggers.

For software work, the output can be a pull request attestation bound to a
commit, test environment, dependency set, tool versions, permission record,
and declared limitations. This can wrap existing coding agents rather than
requiring a new general agent.

The likely durable value is in contract templates, verifier integrations,
evidence histories, policy integration, and trustworthy capability lifecycle
management—not in the choice of graph database or orchestration loop.

## 10. Research sequence

1. Establish the admission and invalidation semantics.
2. Implement the small runtime and test its conditional invariants.
3. Measure an assurance-only system with human-authored contracts.
4. Estimate the upper bound of reusable capability value using manually
   authored guards.
5. Introduce automatic trace slicing and guard inference.
6. Run chronological reuse, near-match, poisoning, and environment-shift tests.
7. Replace and remove the original proposer under fixed registries and budgets.
8. Add a second domain only after the software results survive.

The project advances by surviving increasingly hostile tests, not by expanding
the vocabulary of the vision.
