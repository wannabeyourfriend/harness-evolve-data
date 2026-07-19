# tools — generators for benchmarks_difficulty and benchmarks_difficulty_fmt

Vendored from the harness-evolve repo's (git-ignored) `runs/_drivers/` so the
datasets on this branch stay reproducible without access to that machine.

- `build_difficulty_ladder.py` — builds `benchmarks_difficulty/L{1,2,3}`:
  in-process reuse of the canonical samples builder
  (`harness_evolve.benchmarks.reasoning_gym.samples`) with per-level
  dataset_kwargs and adaptive heldout caps. Run from a harness-evolve
  checkout: `HARNESS_EVOLVE_ALLOW_TEST_SPLIT=1 PYTHONPATH=$PWD python
  runs/_drivers/build_difficulty_ladder.py --levels-json <batch>.json`.
  (Heldout seeds are private-per-build; a rebuild reproduces dev exactly,
  heldout only distributionally.)
- `perturbations/` — the 36 per-task exact-reversible format modules +
  `_common.py` (contract: K, fields/render/parse, per-item round-trip
  verification, i%K rotation, fallback-never-drop) +
  `build_difficulty_fmt.py` (selftest-gated: builds
  `benchmarks_difficulty_fmt` from `benchmarks_difficulty`). Selftest one
  module: `HE_FMT_SRC=<level root> python -m
  runs._drivers.perturbations._common <task>`.

These import the harness-evolve package (schema, samples builder,
number-word helpers) — they are vendored here for provenance and run from
a harness-evolve checkout at the paths above.
