# Stage B: Manual-Reuse Upper-Bound Harness

## 1. Question

Stage B asks a deliberately easier question than automatic capability
promotion:

> If experts supplied correct capability implementations and applicability
> guards, would recurring structure be sufficient to reduce reliance on the
> original proposer after lifecycle costs are counted?

If the manual upper bound has no material value, automatic trace promotion
cannot rescue the competence-migration thesis.

The implementation is in src/jitc/experiment.py. It is an experiment
orchestrator outside the trusted admission kernel.

## 2. Experimental separation

Each evaluation case contains two parts:

- TaskInstance is visible to capabilities and proposers; and
- expected_output is supplied only to the adjudicator.

This is an architectural separation in one Python process, not a secrecy
boundary. A real study must keep hidden adjudication material physically
separate and reveal it only after systems and registry checkpoints are frozen.

At each checkpoint, both conditions receive:

- the identical ordered task set;
- the same immutable capability registry;
- the same online cost ceiling;
- the same deterministic lookup and adjudicator; and
- different proposer interventions.

The current demonstration compares a functionally complete proposer with a
null proposer. The evaluator records the per-task paired utility differences
and reports:

\[
\Delta_M(t)
= U(R_t, M_{\mathrm{original}})
- U(R_t, M_{\mathrm{null}}).
\]

Call reduction alone cannot satisfy this estimand: a cheap proposer that
returns nothing has low cost but zero cold-registry utility.

## 3. Manual capability semantics

A manual capability has:

- one declared task family;
- exact required task attributes and environment values;
- an implementation;
- online execution cost; and
- promotion, validation, and maintenance costs.

Registry selection is deterministic. Exactly one applicable capability may
run. Zero matches, rejected guards, or multiple applicable capabilities route
to the proposer. A failed or independently rejected capability is counted as
negative transfer before proposer fallback. Thus fallback recovery does not
erase a bad reuse attempt.

Lifecycle costs are amortized over an explicit evaluation horizon and included
in all-in cost. The horizon is illustrative in the demonstration and must be
pre-registered for a real study.

## 4. Constructed identification check

The demonstration contains six surface-varied tasks:

- two supported key-normalization tasks;
- one adversarial normalization near-match under a shifted schema;
- two supported integer-version tasks; and
- one genuinely novel redaction family.

Two expert-authored capabilities enter over three chronological snapshots.

| Registry checkpoint | Strong utility | Null utility | Delta M | Strong proposer calls | Reuse precision |
|---|---:|---:|---:|---:|---:|
| cold | 1.000 | 0.000 | 1.000 | 6 | n/a |
| normalization | 1.000 | 0.333 | 0.667 | 4 | 1.000 |
| two families | 1.000 | 0.667 | 0.333 | 2 | 1.000 |

The near-match guard rejects reuse and the novel family remains proposer
dependent, so intervention loss correctly stays above zero.

These numbers are constructed by design. They prove that the harness is
sensitive to the intended mechanism and does not confuse abstention with
competence migration. They are not evidence that real repository tasks recur,
that guards can be inferred, or that automatic promotion works.

## 5. Oracle conveniences and hidden intelligence

This upper-bound demonstration grants the system:

- correct task-family labels;
- expert-authored family implementations;
- expert-authored exact guards;
- an exact-match oracle adjudicator; and
- fixed illustrative costs.

Family classification is itself a potentially difficult inference problem.
The Stage B result must therefore be reported as an oracle-routing upper bound.
Later stages must separately charge for routing, contract creation, validation,
guard inference, retrieval, and registry maintenance.

## 6. Gate for a substantive Stage B result

The next experiment should replace the constructed cases with frozen
repository fixtures containing:

1. at least two repeated latent repair families;
2. surface-diverse held-out instances;
3. adversarial near-matches that must reject reuse;
4. dependency or environment shifts;
5. a novel mechanism with no registered capability; and
6. hidden tests created after the manual capabilities are frozen.

It must report matched direct-agent, workflow, and retrieval-memory baselines;
wall-clock and token costs; accepted utility and coverage; negative-transfer
severity; and confidence intervals clustered by task family. Only then does
Stage B estimate a real reuse upper bound.

The first executable step toward this gate is documented in
[the repository-fixture pilot](repository-pilot.md). It applies strict patches
to temporary worktrees and includes deterministic-workflow and exact-snapshot
retrieval baselines, while retaining explicit oracle and sandbox limitations.
