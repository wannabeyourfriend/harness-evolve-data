# benchmarks_difficulty_fmt — format-varied difficulty ladder (36 tasks x L1-L3)

`benchmarks_difficulty/` with exact-reversible format perturbation applied
to every task at every level (built 2026-07-19). Purpose: anti-degeneration
training data and format-robustness evals — a harness that regex-matches
one canonical lead-in breaks here; a harness that actually reads the
problem does not.

## Mechanism

Per-task perturbation modules (`runs/_drivers/perturbations/` in the
harness-evolve repo; contract in `_common.py`): each module defines
fields/render/parse with machine-checked exact reversibility —
`parse(render(fields(e), v)) == fields(e)` verified per item on every
level's real rows before the build is allowed to write anything. Rotation
`i % K` with **v0 = the original question unchanged** (~1/K of rows are
untouched); verify-failures fall back to the original (never drop) — this
build had **0 fallbacks over 10,770 rows**. `metadata.format_variant`
marks each row's variant; row `input.text`/`provenance.input_sha256` and
the manifests' file sha256 are recomputed; manifests carry a
`format_varied` marker. Answers, ids, and row order untouched.

Hard rules the variants obey: instance data (grids, boards, code blocks,
example blocks, clue lists, histories, expressions) stays byte-verbatim —
only framing prose varies; answer-format directives are never dropped and
never added (an added-directive violation found in audit was fixed and the
set rebuilt); solution-bearing metadata is never read into a question.
Number-word variants are exactly value-preserving. Two designed
exceptions: propositional_logic's word/ASCII-connective variants add a
NOTE restating the pre-existing symbol-answer directive (the notation
switch is unanswerable without it), and circuit_logic relabels wires via
full-alphabet self-inverse maps (ROT13/Atbash) anchored to the two label
positions only.

## Verification

- Machine: 108 (task x level) selftests green (all rows x all variants);
  10,770 rows written, 0 fallbacks (`fmt_build_stats.json`).
- Independent adversarial audit of 120 sampled original/varied pairs
  across all tasks and levels: **120/120 semantically equivalent** —
  arithmetic answers fully recomputed from both texts (incl. word-form
  numbers), grid/board/code/example blocks proven byte-identical, BFS/
  rotation/queens answers re-derived, directive preservation checked per
  pair.

## Notes

- K per task: 3 for all except tower_of_hanoi (K=4). ~2/3 of rows varied.
- Upstream source quirks are preserved in v0 by design (e.g.
  rotten_oranges' "Your task is determine", zebra's double "??",
  simple_geometry's run-together directive, kakurasu's "Kukurasu").
- Multi-template tasks are handled natively (kakurasu samples 1 of 10
  full templates; codeio has predict-input/predict-output modes;
  family_relationships and simple_geometry have 3 templates each;
  knight_swap has w-moves/B-moves subtemplates) — every native surface
  parses and round-trips.
- Counts/level kwargs/provenance: identical to `benchmarks_difficulty/`
  (same rows, reformatted).
