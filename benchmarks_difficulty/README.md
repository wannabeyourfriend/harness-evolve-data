# benchmarks_difficulty — difficulty-laddered task samples (pilot)

Three difficulty levels for 4 reasoning_gym tasks (count_primes,
tower_of_hanoi, propositional_logic, sokoban), built 2026-07-19 with the
same builder, schema, seeds, and generator pin as the canonical
`benchmarks/` splits.

- **L1** = generator defaults = the published reasoning-gym-eval "easy"
  split. **L1 dev files are byte-identical to `benchmarks/dev` at d673f91**
  (verified by sha256) — L1 *is* the canonical distribution.
- **L3** = the published reasoning-gym-eval "hard" config per task
  (pre-validated difficulty bumps).
- **L2** = midpoint between L1 and L3.

Each `L*/` directory is a self-contained dataset root (`dev/`, `heldout/`,
`manifests/`) — point `DATASET_PATH` (or `task_config.dataset_path`) at it
and the evaluator reads the level's `dataset_kwargs` from the manifest, so
scoring matches generation with no pipeline changes.

Counts: dev 25 / heldout 75 per task and level, except tower_of_hanoi
heldout = 60 (its default-config instance space cannot yield 75 unique rows
disjoint from dev; canonical hit the same cap). Dev seed 42; heldout seeds
private per the canonical convention. Generator: reasoning_gym @ e0f181a.
Same heldout count at every level of a task, so cross-level comparisons
share n. Dev/heldout input-hash disjointness verified per level.

## Level kwargs

| task | L2 | L3 (published hard) |
|---|---|---|
| count_primes | min_n 5000, max_n 25000 | min_n 10000, max_n 50000 |
| tower_of_hanoi | disks 4-8 | disks 5-10, pegs 3-4 |
| propositional_logic | vars 3-6, statements 3-6, complexity 2-3 | vars 4-8, statements 4-8, complexity 2-4 |
| sokoban | 8x8-12x12 | 10x10-15x15 |

(L1 = `{}` = defaults.) Measured knob spread in the built dev sets —
tower_of_hanoi max solution length 127 (L1) -> 255 (L2) -> 1023 (L3).

Builder: `runs/_drivers/build_difficulty_ladder.py` in the harness-evolve
repo (in-process reuse of the canonical samples builder with per-level
dataset_kwargs). Extending to the other matrix tasks = adding level dicts
(see harness-evolve `docs/task_difficulty_matrix.md`, 15 tasks mapped).

## Sample questions (dev[0] of each level)

### count_primes

- **L1** (dev[0]): Count how many prime numbers there are between 5611 and 8588 (inclusive) ?
- **L2** (dev[0]): Count how many prime numbers there are between 16221 and 22175 (inclusive) ?
- **L3** (dev[0]): Count how many prime numbers there are between 32443 and 44351 (inclusive) ?

### tower_of_hanoi

- **L1** (dev[0]): Solve the Tower of Hanoi problem with 3 disks and 3 pegs. Move all disks from Peg 3 to Peg 2 following the rules: - Only one disk can be moved at a time. - A larger disk cannot be placed on top of a smaller disk. - All disks must be on a peg at all times. Provide the sequence of moves. Formatting guidelines: - Each ins …
- **L2** (dev[0]): Solve the Tower of Hanoi problem with 4 disks and 3 pegs. Move all disks from Peg 3 to Peg 2 following the rules: - Only one disk can be moved at a time. - A larger disk cannot be placed on top of a smaller disk. - All disks must be on a peg at all times. Provide the sequence of moves. Formatting guidelines: - Each ins …
- **L3** (dev[0]): Solve the Tower of Hanoi problem with 5 disks and 3 pegs. Move all disks from Peg 3 to Peg 2 following the rules: - Only one disk can be moved at a time. - A larger disk cannot be placed on top of a smaller disk. - All disks must be on a peg at all times. Provide the sequence of moves. Formatting guidelines: - Each ins …

### propositional_logic

- **L1** (dev[0]): The following question is a propositional logic reasoning question. In the question we provide a list of premises. The task is to infer a correct conclusion from the premise. FORMAT INSTRUCTIONS: - Return the conclusion logic statement, as your final answer. - Use the following notation to denote symbols - OR = ∨ - AND …
- **L2** (dev[0]): The following question is a propositional logic reasoning question. In the question we provide a list of premises. The task is to infer a correct conclusion from the premise. FORMAT INSTRUCTIONS: - Return the conclusion logic statement, as your final answer. - Use the following notation to denote symbols - OR = ∨ - AND …
- **L3** (dev[0]): The following question is a propositional logic reasoning question. In the question we provide a list of premises. The task is to infer a correct conclusion from the premise. FORMAT INSTRUCTIONS: - Return the conclusion logic statement, as your final answer. - Use the following notation to denote symbols - OR = ∨ - AND …

### sokoban

- **L1** (dev[0]): You are going to solve a 'sokoban' puzzle. * - The player % - The player on a goal @ - A box X - A goal $ - A box on a goal + - A wall - - An empty position Your solution must be a string of characters, ex: LDURRUDL. Here is your puzzle: + + + + + + + * @ X + + + @ - $ + + + - - - - + + - - - - + + - - @ - + + X - X +  …
- **L2** (dev[0]): You are going to solve a 'sokoban' puzzle. * - The player % - The player on a goal @ - A box X - A goal $ - A box on a goal + - A wall - - An empty position Your solution must be a string of characters, ex: LDURRUDL. Here is your puzzle: + + + + + + + + + + - - - - - - - + + - - - - - - X + + - - - $ - - - + + + - - -  …
- **L3** (dev[0]): You are going to solve a 'sokoban' puzzle. * - The player % - The player on a goal @ - A box X - A goal $ - A box on a goal + - A wall - - An empty position Your solution must be a string of characters, ex: LDURRUDL. Here is your puzzle: + + + + + + + + + + + + + + + + - - - - + + + + + + + - - - - - - - - + + $ + + -  …

