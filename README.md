# Just-in-Time Cognition

> **Status:** A research program, not a product. The working note, the adversarial stress test, and the academic pass are complete; the formal core and the experiment harness in `src` are early. The tests cover the core, the contract loader, the state space, the repository adapter, and both experiments. Maintained as notes.

Just-in-Time Cognition (JITC) is a research program for verifier-governed
agents. It asks whether some competence can move from an opaque proposal model
into explicit task contracts, live evidence, permissioned tools, and reusable
capabilities whose validity conditions remain inspectable.

The working rule is:

> Models propose. Contracts constrain. Evidence admits. Dependencies revoke.

This repository now separates three levels of claim:

1. **Kernel guarantees.** Conditional invariants about admission, permissions,
   provenance, and declared-dependency invalidation. These can be specified,
   implemented, and tested now.
2. **Systems hypotheses.** Claims that contracts and evidence-directed planning
   improve reliability or efficiency. These require controlled experiments.
3. **The long-term conjecture.** Reusable verified capabilities may reduce
   dependence on the proposal model over a chronological task stream. This is
   an empirical possibility, not a premise.

The project does not claim prior-free intelligence, open-world truth,
assumption-free reasoning, or the near-term elimination of pretrained models.

## Current artifacts

- [Working note](working-note.md): the original vision and internal debate.
- [Adversarial stress test](academic-stress-test.md): objections, required
  repairs, baselines, and kill criteria.
- [Research proposal](academic-pass.md): the first formalized paper-length pass.
- [Research charter](docs/research-charter.md): the refined thesis and novelty
  boundary.
- [Formal core](docs/formal-core.md): state, transitions, assumptions, and
  conditional theorems.
- [Experiment protocol](docs/experiment-protocol.md): the empirical path from
  assurance wrapper to competence migration.
- [Stage B harness](docs/stage-b-harness.md): paired proposer interventions,
  guarded manual reuse, negative-transfer accounting, and oracle boundaries.
- [Repository-fixture pilot](docs/repository-pilot.md): actual temporary
  worktree patches, behavioral adjudication, and classical baselines.
- [Interactive JIT Compiler visual](docs/jit-compiler-visual.html): architecture,
  trust boundaries, execution trace, dependency revocation, and research stages.

The executable kernel lives under src/jitc. It deliberately excludes language
models, retrieval, planning, and automatic capability generalization. Those
components are outside the trusted core and will be added behind explicit
interfaces only after the admission semantics hold.

## ECIR Stage A

The first end-to-end contract is
[examples/kernel-self-check.ecir.json](examples/kernel-self-check.ecir.json).
It authorizes one content-bound, no-shell repository command. The host hashes
an explicit manifest of input files before and after execution. The command's
exit record and measured environment become an observation, an independent
deterministic verifier turns that observation into evidence, and the runtime
emits either a complete or unresolved evidence envelope.

Run it with:

~~~text
PYTHONPATH=src python3 -m jitc \
  examples/kernel-self-check.ecir.json \
  --repo . \
  --allow-executable python3
~~~

After changing any file named in a command's environment manifest, measure the
new digest before updating the environment object, policy, and command fields:

~~~text
PYTHONPATH=src python3 -m jitc \
  examples/kernel-self-check.ecir.json \
  --repo . \
  --measure-environment
~~~

The extra executable allow-list is a host decision independent of the
contract. The current adapter confines the working directory, binds the token
to the exact command specification, rejects a pre-run environment mismatch,
and refuses admission after an in-run environment change. The two measurements
are not an atomic filesystem snapshot. The adapter is not yet an OS sandbox
and does not block network or other ambient process privileges.

## Verification

Run:

~~~text
python3 -m pytest
~~~

The tests include bounded state-sequence exploration and real no-shell
subprocess execution in addition to ordinary unit tests. Passing tests
demonstrate conformance of this implementation to the specified finite cases;
they do not prove verifier soundness, contract quality, dependency
completeness, process isolation, or the broader JITC research thesis.

## Stage B identification check

The experiment harness under src/jitc/experiment.py evaluates immutable
registry checkpoints with identical task sets and budgets under an original
and an intervention proposer. Run the constructed manual-reuse upper bound:

~~~text
PYTHONPATH=src python3 -m jitc.experiment
~~~

Add --include-outcomes for task-level audit records. The demonstration uses
oracle family labels, expert guards, and an exact adjudicator. Its declining
intervention-loss curve validates the measurement mechanism, not the
competence-migration thesis.

Run the executable trusted-fixture pilot with:

~~~text
PYTHONPATH=src python3 -m jitc.repository_pilot
~~~

This pilot executes patched fixture code and is not an OS sandbox. It is safe
only for the repository's trusted static candidate generators.

## License

Text and notes: CC BY 4.0 (LICENSE). Code: Apache-2.0 (LICENSE-CODE). Attribution: eparenti.
