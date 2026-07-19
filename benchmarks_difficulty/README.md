# benchmarks_difficulty — difficulty-laddered task samples (36 tasks x L1-L3)

Three difficulty levels for 36 reasoning_gym tasks, built 2026-07-19 with
the same builder, schema, dev seed (42), and generator pin (reasoning_gym @
e0f181a) as the canonical `benchmarks/` splits.

- **L1** = generator defaults (the published reasoning-gym-eval "easy"
  configuration). For **33/36 tasks the L1 dev files are byte-identical to
  `benchmarks/dev` at d673f91** (sha256-verified). The other three —
  codeio, knight_swap, word_ladder — are the same configuration and seed
  but not byte-reproducible (generator iteration-order nondeterminism;
  codeio differs even across two local runs with identical seeds), so
  treat their L1 as same-distribution, not per-instance-paired with
  canonical.
- **L3** = the published reasoning-gym-eval hard config where one exists
  (word_ladder, sokoban, tower_of_hanoi, propositional_logic,
  mahjong_puzzle, n_queens, rotten_oranges, emoji_mystery), else a
  curriculum-informed bump (~2 rungs above defaults), smoke-tested per
  task. **L2** = midpoint.
- Excluded (no live difficulty knobs, verified in source): **arc_agi**
  (fixed arckit corpus; rotation/mirror weights are dead under the
  canonical split pins), **acre** (config = split pin only), 
  **list_functions** (uniform sampling over 17 fixed generators).

Each `L*/` directory is a self-contained dataset root (`dev/`, `heldout/`,
`manifests/`): point `DATASET_PATH` (or `task_config.dataset_path`) at it
and the evaluator reads that level's `dataset_kwargs` from the manifest —
scoring matches generation with no pipeline changes.

Counts: dev 25 / heldout 75 per task and level (tower_of_hanoi 65 — its
default-config instance space caps unique disjoint rows; the count is held
equal across a task's levels so cross-level comparisons share n). Dev seed
42; heldout seeds private per the canonical convention. Dev/heldout
input-hash disjointness verified per level; `build_summary.json` carries
per-task/level counts, kwargs, and mean question lengths.

Builder: `runs/_drivers/build_difficulty_ladder.py` in the harness-evolve
repo (in-process reuse of the canonical samples builder; per-level
dataset_kwargs; adaptive heldout-count fallback). Level definitions were
proposed per task from the pinned source's Config + Curriculum and
smoke-tested (create_dataset, monotone dominant knob, generation speed,
uniqueness stress on small-space suspects).

## Level kwargs (L1 = `{}` = defaults)

| task | L2 kwargs | L3 kwargs | heldout n |
|---|---|---|---|
| ab | `{"length":25}` | `{"length":50}` | 75 |
| arc_1d | `{"min_size":20,"max_size":50}` | `{"min_size":40,"max_size":100}` | 75 |
| basic_arithmetic | `{"min_terms":4,"max_terms":8,"min_digits":2,"max_digits":4}` | `{"min_terms":6,"max_terms":10,"min_digits":3,"max_digits":5}` | 75 |
| binary_alternation | `{"min_n":30,"max_n":100}` | `{"min_n":100,"max_n":500}` | 75 |
| boxnet | `{"min_row_num":2,"max_row_num":5,"min_column_num":2,"max_column_num":5,"min_box_num":1,"max_box_num":2}` | `{"min_row_num":3,"max_row_num":6,"min_column_num":3,"max_column_num":6,"min_box_num":2,"max_box_num":4}` | 75 |
| caesar_cipher | `{"min_words":10,"max_words":30}` | `{"min_words":20,"max_words":50}` | 75 |
| circuit_logic | `{"min_terms":5,"max_terms":7,"min_inputs":3,"max_inputs":5}` | `{"min_terms":7,"max_terms":9,"min_inputs":4,"max_inputs":5}` | 75 |
| codeio | `{"difficulty":8}` | `{"difficulty":9}` | 75 |
| color_cube_rotation | `{"min_rotations":4,"max_rotations":6}` | `{"min_rotations":8,"max_rotations":12}` | 75 |
| count_primes | `{"min_n":5000,"max_n":25000}` | `{"min_n":10000,"max_n":50000}` | 75 |
| emoji_mystery | `{"min_words_in_sentence":6,"max_words_in_sentence":32}` | `{"min_words_in_sentence":10,"max_words_in_sentence":30}` | 75 |
| family_relationships | `{"min_family_size":7,"max_family_size":9}` | `{"min_family_size":9,"max_family_size":11}` | 75 |
| group_anagrams | `{"min_anagram_groups":10,"max_anagram_groups":50}` | `{"min_anagram_groups":50,"max_anagram_groups":100,"max_words_per_group":10}` | 75 |
| jugs | `{"difficulty":15}` | `{"difficulty":20}` | 75 |
| kakurasu | `{"min_rows":5,"max_rows":6,"min_cols":5,"max_cols":6}` | `{"min_rows":6,"max_rows":7,"min_cols":6,"max_cols":7}` | 75 |
| knight_swap | `{"min_nodes":8,"max_nodes":10}` | `{"min_nodes":10,"max_nodes":12,"min_pieces":3,"max_pieces":3,"max_steps":30}` | 75 |
| leg_counting | `{"min_animals":5,"max_animals":15,"max_instances":32}` | `{"min_animals":8,"max_animals":20,"max_instances":64}` | 75 |
| letter_jumble | `{"min_words":10,"max_words":30,"min_corruption_level":0.3}` | `{"min_words":20,"max_words":50,"min_corruption_level":0.6}` | 75 |
| mahjong_puzzle | `{"min_num_rounds":30,"max_num_rounds":75}` | `{"min_num_rounds":50,"max_num_rounds":100}` | 75 |
| maze | `{"min_dist":10,"max_dist":15,"min_grid_size":15,"max_grid_size":25}` | `{"min_dist":15,"max_dist":20,"min_grid_size":25,"max_grid_size":50}` | 75 |
| mini_sudoku | `{"min_empty":10,"max_empty":12}` | `{"min_empty":12,"max_empty":12}` | 75 |
| modulo_grid | `{"max_holes":5}` | `{"max_holes":10}` | 75 |
| n_queens | `{"n":8,"min_remove":3,"max_remove":6}` | `{"n":8,"min_remove":4,"max_remove":6}` | 75 |
| palindrome_partitioning | `{"min_string_len":10,"max_string_len":18}` | `{"min_string_len":12,"max_string_len":22}` | 75 |
| polynomial_equations | `{"min_degree":2,"max_degree":3,"min_terms":3,"max_terms":5}` | `{"min_degree":3,"max_degree":4,"min_terms":4,"max_terms":6}` | 75 |
| power_function | `{"min_exponent":2,"max_exponent":10}` | `{"min_exponent":4,"max_exponent":12}` | 75 |
| propositional_logic | `{"min_vars":3,"max_vars":6,"min_statements":3,"max_statements":6,"min_complexity":2,"max_complexity":3}` | `{"min_vars":4,"max_vars":8,"min_statements":4,"max_statements":8,"min_complexity":2,"max_complexity":4}` | 75 |
| rotten_oranges | `{"min_n":18,"max_n":40}` | `{"min_n":25,"max_n":50}` | 75 |
| shortest_path | `{"min_rows":8,"max_rows":12,"min_cols":8,"max_cols":12}` | `{"min_rows":15,"max_rows":25,"min_cols":15,"max_cols":25}` | 75 |
| simple_geometry | `{"min_sides":5,"max_sides":10}` | `{"min_sides":10,"max_sides":15}` | 75 |
| sokoban | `{"min_w":8,"max_w":12,"min_h":8,"max_h":12}` | `{"min_w":10,"max_w":15,"min_h":10,"max_h":15}` | 75 |
| sudoku | `{"min_empty":35,"max_empty":45}` | `{"min_empty":50,"max_empty":60}` | 75 |
| syllogism | `{"invalid_ratio":0.4,"inversion_probability":0.15}` | `{"invalid_ratio":0.5,"inversion_probability":0.0}` | 75 |
| tower_of_hanoi | `{"min_disks":4,"max_disks":8}` | `{"min_disks":5,"max_disks":10,"min_pegs":3,"max_pegs":4}` | 65 |
| word_ladder | `{"min_word_length":4,"max_word_length":5}` | `{"min_word_length":3,"max_word_length":5}` | 75 |
| zebra_puzzles | `{"num_people":5,"num_characteristics":5}` | `{"num_people":6,"num_characteristics":6}` | 75 |

## Per-task caveats (from the knob survey)

- **basic_arithmetic**: Near-ceiling task; defaults (terms 2-6, digits 1-4) already occupy the FULL curriculum ladder (num_terms [2..6], num_digits [1..4]), so a real bump must exceed the curriculum: L2/L3 raise both floor and ceiling on terms (dominant) plus a modest digits bump (both are curriculum attributes, so coupled). L3 answers reach 15-17 digits (multi-digit products), expressions ~65-100 chars with nested parens/negation. Division stays exact (generator picks common divisors). Smoke: instant at all levels.
- **caesar_cipher**: Rotation is hard-capped [1,25] by Config.validate and defaults already span it (the curriculum's rotation rung 50 is invalid), so sentence length is the only real knob; curriculum words rungs [5,15,25,50]. Sentence pool at 20-50 words = 130 sentences x 25 rotations - n=100 stress gave 96/100 unique questions (small dup rate, acceptable; flag if sampling >>100 rows). Answer is exact-match text up to ~300 chars at L3. Canonical template untouched.
- **circuit_logic**: DIALED BACK from the curriculum 2-rungs-up choice: terms rung ladder is [3,5,10,20,30] and inputs [2,4,6,8,10], but terms(7,10)+inputs(4,6) tails at 8009-char questions (n=300 across seeds 1-3), over the ~8k cap for 32k-token solvers. Measured question lengths (n=300, seeds 1-3): defaults ~371-1418 (mean ~823 at n=20); L2 (5-7 terms, 3-5 inputs) min/mean/max 1072/1826/3057; final L3 (7-9 terms, 4-5 inputs) min/mean/max 1706/3389/5070 - comfortable margin, ASCII diagram is the dominant length driver (width grows ~2 cols per distinct input). Monotone on dominant knob terms: 3-5 < 5-7 < 7-9; inputs 2-4 <= 3-5 <= 4-5. Smoke-tested both levels: pass, instant generation.
- **codeio**: Corpus-backed but difficulty IS parameterized: CodeIOConfig.difficulty (1-10) filters the source pool by a per-program difficulty label. Pool sizes: d7=393, d8=2025, d9=54, unlabeled=494, easier<=6 rare. Default (difficulty=None) mixes all 3002 entries and is already ~67% d8, so L2=8 is a mild bump (drops the 494 unlabeled + 393 d7 + easier tail); L3=9 is the hard end. SMALL INSTANCE SPACE at L3: only 54 distinct source programs at d9 (samples drawn with replacement; watch dev/heldout dedup pressure). Question lengths: d8 max ~6.8k chars, d9 max ~10-14k chars (~3-4k tokens, fine for 32k solvers). Some source snippets print to stdout during generation-time exec (upstream behavior, harmless). Smoke-tested size=5 and size=25 on both levels: no crashes, no empty IO pairs, <0.2s.
- **emoji_mystery**: L3 = published hard from docs/task_difficulty_matrix.md (raises the sentence-length floor 3->10); L2 = midpoint (6,32). Doc caveat: BOTH splits are near-saturated-hard for plain LLMs (variation-selector decoding); the ladder is meaningful for harness+solver systems where code can decode. Sentence pool: 481/369/251 sentences at L1/L2/L3 x 109 emojis - no uniqueness risk (100/100 unique).
- **jugs**: Dominant knob = difficulty (min BFS moves; also raises jug capacity cap 3+difficulty), curriculum [5,10,15,20]; default 10 = rung 1, L2 = rung 2, L3 = rung 3. num_jugs deliberately kept at 3: the pinned generate_jug_solution() is HARDCODED to 3 jugs (initial_state=(0,0,0), range(3)), so num_jugs>3 silently corrupts oracle answers - do not raise it on this pin. Measured min_moves: L1 [10..15], L2 [15..24], L3 [21..33]; oracle answers ~280-320 chars JSON at L3 (solver must emit ~25-35 moves). Smoke: 10 instances in 0.2s at L3.
- **kakurasu**: Dominant knob rows/cols (curriculum [4,6,7,9]); L3 = rung 7, two above default 4-5 band; p_ones left at default 0.3 (uniqueness search stays fast). Config caps rows/cols at 9. Smoke ok, 120/120 unique at L3 in 0.3s.
- **knight_swap**: Dominant knobs nodes (curriculum [4,6,8,10,12]) + pieces; generation uses min_pieces as the fixed piece count, so min=max=3 at L3; max_steps raised to next curriculum rung (30) so 3-piece solutions (20-24 steps observed) are not rejected. Smoke ok (~0.8s/item at L3, 120/120 unique). Flag: board pool is only 12 candidate squares (A1-D3), so node-set variety at 10-12 nodes is small (79 subsets); variety comes from piece placement - 120 unique questions confirmed but do not push far past a few hundred.
- **leg_counting**: Small-knob concern checked and CLEARED: instance space is 37 animal types x counts, 100/100 unique questions at L1, L2, and L3 (seed 7). Both curriculum knobs bumped: num_animals (fine-grained ladder 1..36; more terms to sum) and max_instances (curriculum ladder [2,4,...,1024]; default 15 -> 32 -> 64 = ~2 rungs, bigger per-term products). Answers grow 44-554 (L1) -> 152-1566 (L2) -> 806-3579 (L3). min_instances kept 1. Stopped at 64 instances to keep totals in the low thousands rather than turning it into pure big-number addition. Smoke: instant.
- **mini_sudoku**: Dominant knob min_empty/max_empty, but config hard-caps empties at 12 for uniqueness and the DEFAULT already spans 8-12, so only floor-lifting is possible; L3 pins all instances at the 12-empty ceiling (curriculum top rung). Difficulty delta over defaults is modest. Smoke ok; 120/120 unique questions even at fixed 12 empties (4x4 has 288 solved grids x mask choices).
- **modulo_grid**: Dominant knob = max_holes (inference burden), curriculum ladder [1,5,10,15]; L3 = 2 rungs above default 1. Grid size deliberately kept at default 20x20: the answer must reproduce the ENTIRE emoji grid (400 cells, ~419 chars already), so bumping size_x/size_y (curriculum [20,40,60,80]) quadruples question+answer tokens and confounds difficulty with output-length/truncation. max_divisor/max_target kept at defaults (20/20, already above most curriculum rungs). Caveat: holes are punched at random cells with replacement, so actual holes can be slightly < max_holes on collisions. Smoke: instant, qlen/alen stable ~581/419 at all levels.
- **palindrome_partitioning**: DIALED BACK from curriculum-implied (15-25): the oracle answer enumerates ALL partitions and grows exponentially in string_len - (15-25) hit p99=169KB/max=236KB answers at n=200, which no solver can emit within token clamps. Chosen rungs: L1 p99=6.6KB, L2 (10-18) p99=18KB, L3 (12-22) p99=53KB - already punishing but bounded. max_substring_palindrome_len left at default 5 (raising it multiplies the explosion). Canonical template untouched.
- **shortest_path**: Dominant knob = grid size (curriculum rows/cols [10,25,50,100]; defaults 5-8 below rung 0; L2 straddles rung 0, L3 tops out at rung 1 = 25). p_blocked kept at default 0.4 (not a curriculum attribute). FLAG: p_open=0.6 is near the site-percolation threshold (~0.593), so the infeasible fraction drifts up with size: 11/30 (L1) -> 14/30 (L2) -> 16/30 (L3, seed 7). A guess-'infeasible' policy scores ~0.5 at L3 (vs ~0.37 at L1) - though proving infeasibility on a 25x25 grid is itself nontrivial. Feasible-path lengths grow to 14-27 moves at L3; question ~1.1-1.6KB. Smoke: instant.
- **sudoku**: Dominant knob min_empty/max_empty (config caps at 64); bands from our 4B prior art (1.00 at ~20-30, 0.30 at 35-45, 0.02 at 50-60), matching curriculum rungs [20..60]. Smoke ok; L3 generation slower (~0.13s/item, 120/120 unique) but fine.
- **syllogism**: FLAG: narrow difficulty range. The curriculum only ramps the quantifier set (allow_*), and defaults already have all four enabled = curriculum max, so no structural rung above defaults exists. Remaining monotone levers: invalid_ratio 0.3->0.4->0.5 (kills the always-Yes majority prior: measured Yes-rate 70/100 -> 56 -> 46) and inversion_probability 0.3->0.15->0.0 (single-premise inversion items are the easy subclass; L3 is 100% two-premise syllogisms requiring Aristotelian distribution rules). Answer stays Yes/No - no format change. Expect a modest, not dramatic, L1->L3 gap.
- **word_ladder**: L3 = published hard from docs/task_difficulty_matrix.md; L2 = midpoint (4-5). max_word_length is hard-capped at 5 by Config.validate. Difficulty comes from sparser 5-letter word graphs (n=100 stress: chains up to 113 chars vs ~40 at default). Caveat: L3's min=3 admits some easy 3-letter instances (dense graph) - that is what the published-hard split does. Smoke: 100/100 unique questions, 0.4s per 100 rows.
- **zebra_puzzles**: Curriculum rungs = 2..7 on both scalars; default 4x4, L3 6x6 = 2 rungs above on each, L2 5x5 between (config hard-caps at 7). Generation time is the binding constraint: 4x4 0.3s, 5x5 1.4s, 6x6 6.9s for size=5 (~1.4s/instance, well under budget; 7x7 not attempted since 6x6 already satisfies the 2-rungs target). Question lengths: ~1.2k chars default, ~1.6k at L2, ~2.4k at L3. Smoke-tested both levels, size=5: pass; clue count grows from ~10 to ~19+.
