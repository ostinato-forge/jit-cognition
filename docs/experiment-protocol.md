# Experiment Protocol

## 1. Objective

The experiment must distinguish three outcomes:

1. **No useful mechanism:** the runtime adds cost without improving independent
   validity or safety.
2. **Assurance wrapper:** the runtime reduces false acceptance and improves
   auditability but does not reduce dependence on a strong proposal model.
3. **Competence migration:** validated reusable capabilities preserve utility
   while the original proposer becomes causally less important on new tasks.

The third outcome is the larger JITC result. The second remains a potentially
valuable product but does not establish a new locus of intelligence.

## 2. Initial domain

Begin with repository tasks that are narrower than arbitrary bug repair:

- dependency and language-version upgrades;
- mechanical API migrations with behavioral tests;
- reproducible build and test failures;
- configuration faults with executable acceptance checks; and
- bounded data-pipeline repairs.

These tasks provide sandboxable effects, partially independent checks,
repeated latent structure, and controllable environmental shift.

Root-cause explanations should not be labeled mechanically verified merely
because a patch passes. They require a separate causal-evidence policy, such as
discriminating intervention, revert-and-reproduce checks, or hidden mechanism
tests.

## 3. Staged evaluation

### Stage A: Runtime semantics

Use human-authored contracts, hand-authored capabilities, and deterministic
verifiers.

Question: Does explicit admission reduce false accepted claims and unauthorized
actions without intolerable overhead?

This stage isolates the runtime from contract-generation and automatic
generalization errors.

### Stage B: Reuse upper bound

Allow manually generalized capabilities with expert-authored guards and hidden
validation.

Question: If guards were good, is there enough recurring structure for
capability reuse to create material benefit?

If the answer is no, automatic trace promotion cannot rescue the thesis.

### Stage C: Automatic trace promotion

Introduce trace slicing, parameterization, candidate guard inference, negative
tests, held-out tests, shadow execution, versioning, and revocation.

Question: How much of the manual-guard upper bound survives automatic
promotion, including validation and maintenance cost?

### Stage D: Competence migration

Freeze or version the registry at defined checkpoints, then replace the
original proposer with weaker, different, retrieval-only, enumerative, and null
proposers.

Question: Does performance loss from proposer intervention decline as the
registry matures?

## 4. Experimental units

Construct latent task families rather than a bag of unrelated benchmark
instances. Each family should contain:

- training-stream instances;
- surface-diverse held-out instances;
- adversarial near-matches where reuse should be rejected;
- a dependency or environment shift;
- at least one genuinely novel mechanism absent from the registry; and
- a hidden adjudication package.

A pilot may use 10 families with 5 to 8 instances each. A confirmatory study
should be powered over repositories and task families, not repeated attempts
on the same defect. At least one evaluation suite must be created after the
runtime and promotion rules are frozen.

Public benchmarks may be included for comparability but cannot carry the
competence-migration conclusion because of training contamination and template
leakage.

## 5. Systems and baselines

All learned systems receive the same base model, context budget, tools,
documentation corpus, permissions, and total cost ceiling unless the
intervention explicitly changes the proposer.

Required comparisons:

1. ordinary tool-using model loop;
2. plan-and-execute agent with retries/reflection;
3. agent plus ordinary retrieval memory and cached solutions;
4. deterministic workflow or HTN planner;
5. blackboard-style system using the same tools;
6. provenance-aware rule or Datalog engine;
7. CEGIS/program-synthesis baseline where the task DSL permits it;
8. incremental build/query engine for invalidation microbenchmarks;
9. JITC with contracts and admission but no capability promotion;
10. JITC with manual promotion;
11. JITC with automatic promotion; and
12. oracle-contract and oracle-retrieval upper bounds.

The classical baselines are essential. A systems contribution is not supported
if the gains come from rediscovering build-system or workflow behavior behind
new terminology.

## 6. Primary outcomes

Pre-register the following:

- independently adjudicated task utility;
- false-admission or verifier-escape rate;
- contract error rate;
- unauthorized action attempts and successful effects;
- strong-proposer calls, tokens, latency, and cost per valid task;
- external observations and tool calls;
- sequential epistemic depth;
- all-in cost including contract creation, retrieval, guard checks, promotion,
  validation, invalidation, and registry maintenance;
- capability reuse precision and recall;
- negative-transfer severity;
- invalidation precision and recall;
- registry size, redundancy, lookup latency, and maintenance cost; and
- unresolved-output calibration.

Report accepted-task utility and coverage together. A system that achieves zero
false acceptance by refusing everything has not succeeded.

## 7. Causal model-dependence measures

The earlier call-share metric is descriptive but not sufficient. A model can
remain causally essential despite fewer visible calls.

At registry checkpoint \(t\), define:

\[
\Delta_M(t)
= U(R_t, M_{\mathrm{original}})
- U(R_t, M_{\mathrm{intervention}})
\]

where \(U\) is independently adjudicated utility under matched budgets and
\(M_{\mathrm{intervention}}\) is a weaker, different, retrieval-only, or null
proposer.

Competence migration requires:

1. declining strong-proposer cost per independently valid task;
2. declining intervention loss \(\Delta_M(t)\);
3. stable or improving held-out utility and coverage;
4. no equivalent hidden model cost in retrieval, verification, or contract
   generation; and
5. positive net utility after capability lifecycle cost.

Use repeated interventions at chronological checkpoints rather than comparing
only the beginning and end.

## 8. Factorial decomposition

At minimum, cross these factors:

- human-authored versus model-elaborated contracts;
- cold versus warmed registry;
- strong versus weak proposer;
- manual versus automatic capability guards;
- stable versus shifted environment; and
- ordinary versus adversarial near-match tasks.

This separates contract error, planning value, reuse value, proposer value, and
shift robustness instead of attributing every effect to the whole architecture.

## 9. Verifier independence record

For every acceptance decision, record whether supporting checks differ in:

- authority or author;
- model family;
- implementation;
- mechanism;
- data source;
- specification source; and
- hidden versus proposer-visible test material.

Do not collapse these dimensions into one independent-verifier Boolean.
Correlated checks should be analyzed as a shared failure cluster.

## 10. Kill criteria

The central systems hypothesis is unsupported if, after competent
implementation:

1. the full runtime does not reduce false admission or improve independent
   task utility over a matched strong agent;
2. apparent efficiency disappears under all-in accounting;
3. reuse helps only verbatim or trivially parameterized repetitions;
4. near-match transfer precision is worse than the direct-agent baseline;
5. automatic promotion has non-positive net utility after validation and
   maintenance;
6. registry cost grows approximately linearly while marginal reuse approaches
   zero;
7. environment shift cannot be localized through declared dependencies;
8. contract errors dominate execution errors outside hand-crafted examples;
9. proposer intervention loss does not decline over chronological checkpoints;
10. hidden learned components replace rather than reduce the measured proposer
    dependence;
11. high-level obligations are accepted mainly by the same model family that
    proposed them; or
12. the only gains occur in domains with near-perfect executable oracles while
    broad open-world claims remain.

## 11. Positive evidence thresholds

The first credible result is:

> Under matched tools, proposer, and total cost, JITC materially reduces false
> acceptance while preserving useful completion on held-out shifted tasks.

The stronger result is:

> Guarded capabilities produce positive net transfer on surface-diverse,
> structurally related tasks and reject adversarial near-matches.

The distinctive result is:

> Across chronological registry checkpoints, both strong-proposer cost and
> causal proposer-intervention loss decline without loss of held-out utility,
> independent validity, or registry maintainability.

Only the third result supports the claim that competence has begun to migrate.

## 12. Statistical analysis

- Freeze inclusion criteria, budgets, and primary outcomes before the
  confirmatory suite is revealed.
- Use paired comparisons on identical tasks.
- Cluster uncertainty by repository and latent task family.
- Report confidence intervals and full Pareto fronts rather than only means.
- Model time-to-validity with survival analysis when tasks can time out.
- Report learning curves over chronological checkpoints.
- Preserve failed, unresolved, and retracted runs; do not condition analysis
  only on accepted artifacts.
- Publish the registry snapshots and promotion costs required to reproduce each
  checkpoint.

The empirical claim succeeds only if it survives honest accounting and
distribution shift.
