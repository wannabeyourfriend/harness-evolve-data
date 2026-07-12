---
pretty_name: Harness Evolve Data
license: other
language:
- en
tags:
- agent-evaluation
- benchmark
- reasoning
---

# Harness Evolve Data

Private artifact repository for `harness-evolve`. The Hugging Face mirror is
`wannabeyourfriend-hf/harness-evolve-data`; the GitHub repository remains the source used by
the code repository's `data/` submodule.

## Layout

- `benchmarks/`: canonical task-sample envelopes, split manifests, schema, and catalog.

Legacy `problem_splits/` (fixed reasoning-gym experiment splits) and
`sft_training/` (proposer training artifacts) were removed on 2026-07-12; they
remain available in git history and on the Hugging Face mirror.

`benchmarks/heldout/` is reporting-only. The code repository blocks proposer
sessions from reading the whole data submodule and requires an explicit
reporting authorization before heldout loaders run.

## Licensing

This is a mixed-license collection. Each benchmark manifest records its own
source, immutable revision, and license. In particular, AIME 2026 is
CC BY-NC-SA 4.0 and LoCoMo is CC BY-NC 4.0. No repository-wide permissive
license is asserted for the bundled source data.
