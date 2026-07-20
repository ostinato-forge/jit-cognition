# Executable Repository-Fixture Pilot

## 1. Purpose

The repository pilot moves the Stage B identification check from returned
strings to actual file transformations. It remains a constructed upper-bound
experiment, but every candidate is now:

1. encoded as a strict patch set;
2. applied to a fresh temporary worktree;
3. checked against a complete hidden expected snapshot; and
4. subjected to a no-shell behavioral command.

The implementation is in src/jitc/repository_pilot.py. The emitted
benchmark-definition digest commits to visible fixtures, hidden expected
snapshots, hidden commands, task metadata, registry metadata, intervention
conditions, and illustrative costs. It does not hash Python implementation
functions; the Stage A repository environment digest separately binds the
source that executed the pilot.

The frozen v0.1 definition digest is
sha256:bf951d6083a987fc4f8e4ce311ed2c626d84ec5303f2d4816320476926499060.
The test suite pins this value; intentional benchmark changes require an
explicit version and digest update.

## 2. Pilot task structure

The six frozen constructed cases contain:

- two configuration-key migrations with different JSON shapes;
- one shifted-schema near-match where the apparent key must remain unchanged;
- two Python API-provider migrations using direct and aliased imports; and
- one novel output-delimiter task with no registered capability.

The first registry checkpoint is empty. A guarded configuration capability is
added at the second checkpoint and a guarded API capability at the third.
Correct family labels and environment metadata are supplied as oracle inputs.

Patch candidates may modify only existing regular files through canonical
relative paths. Absolute paths, parent traversal, aliases, duplicate targets,
new files, and symlink targets are rejected.

## 3. Conditions

Every condition receives the same six cases in the same order:

- direct strong proposer;
- deterministic workflow;
- exact-snapshot retrieval memory;
- null proposer;
- manual registry plus strong proposer at each checkpoint; and
- manual registry plus null proposer at each checkpoint.

The deterministic workflow is intentionally capable. Classical automation is
a core baseline, not a straw man. Its authored lifecycle cost is amortized by
the same accounting mechanism used for registered capabilities.

## 4. Constructed results

### Intervention curve

| Checkpoint | Strong coverage | Null coverage | Intervention loss | Strong calls | Strong all-in cost |
|---|---:|---:|---:|---:|---:|
| cold | 1.000 | 0.000 | 1.000 | 6 | 6.42 |
| config capability | 1.000 | 0.333 | 0.667 | 4 | 5.52 |
| config + API capabilities | 1.000 | 0.667 | 0.333 | 2 | 4.72 |

The shifted near-match and novel family preserve nonzero intervention loss.
An intentionally over-broad guard produces a rejected capability result,
records negative transfer, and then recovers through the strong proposer.

### Cold-registry baselines

| Condition | Coverage | All-in cost |
|---|---:|---:|
| direct strong proposer | 1.000 | 6.42 |
| deterministic workflow | 0.833 | 2.77 |
| exact-snapshot retrieval | 0.333 | 1.10 |
| null proposer | 0.000 | 0.42 |

The classical workflow is the important result. It captures most utility at
far lower illustrative cost than the direct proposer and nearly the same cost
as the null-proposer warmed registry. JITC cannot claim a distinctive systems
gain unless broader guarded reuse beats or complements this baseline on
held-out real tasks after real authoring and maintenance costs are measured.

## 5. What this establishes

The pilot establishes that the experimental machinery can:

- perform and adjudicate actual repository file effects;
- distinguish surface-diverse reuse from exact snapshot retrieval;
- reject a declared environment near-match;
- retain proposer dependence for novel work;
- expose negative transfer even when fallback repairs the final answer;
- compare matched conditions at immutable checkpoints; and
- include non-model baseline lifecycle cost.

It does not establish that real repositories contain enough reusable
structure, that family routing is cheap, that the illustrative costs are
accurate, or that automatically inferred guards transfer.

## 6. Security boundary

The hidden behavioral command can execute patched Python code. Temporary
directories and path confinement are not an OS sandbox. This runner is
therefore restricted to trusted static fixtures and trusted candidate
generators. It must not execute arbitrary model-generated patches until a
separate syscall, network, credential, and resource isolation boundary exists.

## 7. Next empirical gate

A credible Stage B study now requires externally stored repository snapshots
and post-freeze hidden tests, multiple repositories per latent family,
randomized task order, wall-clock and token accounting, and uncertainty
clustered by family and repository. Family labels should be removed or their
routing cost measured as a separate intervention. The deterministic workflow
must remain in the comparison.
