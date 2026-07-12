# LiveCodeBench source deltas

The builder consumes `test5.jsonl` (v5 delta, 167 rows, 557 MB) and
`test6.jsonl` (v6 delta, 175 rows, 134 MB) from this directory. They are
not tracked in git: fetch them from
`https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/main/test5.jsonl`
(and `test6.jsonl`), then verify against the sha256 values pinned in
`../../manifests/livecodebench/livecodebench.json`.
