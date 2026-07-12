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
- `sources/<benchmark>/`: pinned runtime assets required by an evaluator but
  omitted from its Python package (currently TAU2 policies and databases).
- `catalog.json`: generated inventory of every materialized dataset.

Candidate harnesses receive only the public `input` and `environment` fields.
The referee retains `oracle` and provenance. The catalog currently includes:

| Benchmark | Dev | Held out | Source policy |
|---|---:|---:|---|
| Reasoning Gym | 25 per each of 74 families | 75 per family (tower_of_hanoi 60: instance-space cap) | pinned SSRM generator revision; exact input disjointness; dev seed 42, heldout seed 20260712 |
| Reasoning Gym Mix | 25 (25 distinct families, 1 each) | 75 (remaining 49 families, round-robin ≤2 each) | derived re-index of the frozen per-family splits (no new generation); family-disjoint dev/heldout for task-type transfer; parent-split sha256s pinned; family seed 42, heldout seed 20260712 |
| GoEmotions | 25 | 75 | official validation/test splits; 30 labeled train-pool rows |
| LoCoMo | 3 conversations / 692 QAs | 7 conversations / 1,294 QAs | conversation-disjoint; CC BY-NC 4.0; only 10 conversations exist |
| TAU2 | airline 12, retail 25, telecom 25 | airline 38, retail 75, telecom 75 | task-ID disjoint (airline pool is 50 tasks, kept at 1:3); official v0.2 simulator; heldout seed 707122026 |
| AIME | 25 (2022-2023) | 75 (2024-2026, all 30 of 2026 forced) | multi-year; temporally disjoint (max dev 2023 < min heldout 2024); 2026 is the uncontaminated slice; AI-MO Apache-2.0 (2022-2024) + MathArena CC BY-NC-SA 4.0 (2025-2026); dev seed 42, heldout seed 20260712 |
| Terminal-Bench 2 | 25 | 64 | all 89 public tasks, stratified by category and difficulty |
| SWE-bench Verified | 25 | 75 | repository-disjoint; gold patches are not redistributed |
| LiveCodeBench | 25 (release_v5 delta, 2024-09..2025-01) | 75 (release_v6 delta, 2025-01..2025-04) | temporal disjointness across the release boundary; tests embedded in oracle payloads (private tests keep the lite encoding); dataset card license "cc" without a stated variant |

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
