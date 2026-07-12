# Benchmark data

This directory is the frozen data boundary for unified benchmark experiments.
Every JSONL row follows [`schema/task_sample.schema.json`](schema/task_sample.schema.json).

- `train_pool/<benchmark>/`: labeled examples available to learning harnesses.
- `dev/<benchmark>/`: training-visible evaluation data.
- `heldout/<benchmark>/`: reporting-only data. Loaders require
  `HARNESS_EVOLVE_ALLOW_TEST_SPLIT=1`, and proposer sandboxes cannot read this
  directory.
- `manifests/<benchmark>/`: pinned source, license, sampling configuration,
  counts, hashes, and leakage checks.
- `catalog.json`: generated inventory of every materialized dataset.

Candidate harnesses receive only the public `input` and `environment` fields.
The referee retains `oracle` and provenance. The catalog currently includes:

| Benchmark | Dev | Held out | Source policy |
|---|---:|---:|---|
| Reasoning Gym | 10 per each of 74 families | 30 per family | pinned SSRM generator revision; exact input disjointness |
| GoEmotions | 10 | 30 | official validation/test splits; 30 labeled train-pool rows |
| LoCoMo | 3 conversations / 692 QAs | 7 conversations / 1,294 QAs | conversation-disjoint; CC BY-NC 4.0 |
| TAU2 | 10 per domain | 30 per domain | airline, retail, and telecom task-ID disjoint splits; official v0.2 simulator |
| AIME 2026 | — | all 30 problems | reporting-only; MathArena release; CC BY-NC-SA 4.0 |
| Terminal-Bench 2 | 30 | 59 | all 89 public tasks, stratified by category and difficulty |
| SWE-bench Verified | 10 | 30 | repository-disjoint; gold patches are not redistributed |

Use the benchmark-local builders to regenerate data. Network-backed builders
pin immutable upstream revisions and require the optional data dependencies.

```bash
uv sync --extra data
uv run python -m harness_evolve.benchmarks.reasoning_gym.samples build
uv run python -m harness_evolve.benchmarks.tau2.samples
uv run python -m harness_evolve.benchmarks.aime.samples
uv run python -m harness_evolve.benchmarks.text_classification.samples --force
uv run python -m harness_evolve.benchmarks.locomo.samples --force
uv run python -m harness_evolve.benchmarks.swe_bench.samples --force
uv run python -m harness_evolve.benchmarks.terminal_bench.samples \
  /path/to/exported/terminal-bench-2 --force
uv run python -m harness_evolve.benchmarks.catalog
```

Builders refuse to overwrite frozen outputs unless `--force` is explicit.
Reasoning Gym generation runs each family in a child process, and all builders
record split hashes plus benchmark-appropriate group-disjointness invariants.
