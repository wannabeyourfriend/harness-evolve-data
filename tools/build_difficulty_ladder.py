"""Build difficulty-laddered reasoning_gym datasets (L1-L3 per task).

Levels: L1 = generator defaults (== the published easy split; canonical
distribution), L3 = published hard config where one exists (pre-validated by
reasoning-gym-eval) else curriculum-informed bump, L2 = midpoint. The pilot
4 tasks are inline; larger batches are merged from --levels-json files
(produced by the knob-survey subagents), format:
    {"<task>": {"L2": {...}, "L3": {...}} | {"exclude": "reason"}}

Mechanism: monkeypatch samples._dataset_kwargs (the per-task kwargs hook the
canonical builder consults) and call samples._worker_build in-process per
task x level. Each level directory is a self-contained dataset root
(dev/heldout/manifests) usable via DATASET_PATH; manifests record the level
kwargs, and the generic evaluator loads scoring kwargs from the manifest, so
scoring matches generation with zero pipeline changes.

Heldout counts adapt: tasks whose instance space cannot yield the requested
unique disjoint rows fall back to the achievable count (>= --min-test-count,
else the task is dropped and reported). The SAME heldout count is used at
every level of a task so cross-level comparisons share n.

Heldout seed follows the canonical private-seed convention (secrets, not
recorded). Dev seed 42 as canonical. Needs HARNESS_EVOLVE_ALLOW_TEST_SPLIT=1
(build/validation context: this script CREATES the heldout files).

Usage:
    HARNESS_EVOLVE_ALLOW_TEST_SPLIT=1 PYTHONPATH=$PWD python \
        runs/_drivers/build_difficulty_ladder.py \
        [--levels-json f1.json f2.json ...] [--out data_difficulty] [--force]
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harness_evolve.benchmarks.reasoning_gym import samples  # noqa: E402
from harness_evolve.benchmarks.schema import load_jsonl  # noqa: E402

# Pilot levels (docs/task_difficulty_matrix.md). L1 {} == defaults == easy.
LEVELS: dict[str, dict[str, dict]] = {
    "count_primes": {
        "L2": {"min_n": 5_000, "max_n": 25_000},
        "L3": {"min_n": 10_000, "max_n": 50_000},  # published hard
    },
    "tower_of_hanoi": {
        "L2": {"min_disks": 4, "max_disks": 8},
        "L3": {"min_disks": 5, "max_disks": 10, "min_pegs": 3, "max_pegs": 4},  # hard
    },
    "propositional_logic": {
        "L2": {
            "min_vars": 3, "max_vars": 6,
            "min_statements": 3, "max_statements": 6,
            "min_complexity": 2, "max_complexity": 3,
        },
        "L3": {  # published hard
            "min_vars": 4, "max_vars": 8,
            "min_statements": 4, "max_statements": 8,
            "min_complexity": 2, "max_complexity": 4,
        },
    },
    "sokoban": {
        "L2": {"min_w": 8, "max_w": 12, "min_h": 8, "max_h": 12},
        "L3": {"min_w": 10, "max_w": 15, "min_h": 10, "max_h": 15},  # published hard
    },
}

_COLLECTED_RE = re.compile(r"collected (\d+) after")


def load_levels(paths: list[Path]) -> tuple[dict[str, dict[str, dict]], dict[str, str]]:
    levels = {t: dict(v) for t, v in LEVELS.items()}
    excluded: dict[str, str] = {}
    for path in paths:
        for task, spec in json.loads(path.read_text()).items():
            if "exclude" in spec:
                excluded[task] = spec["exclude"]
                continue
            if task in levels:
                print(f"note: {task} already defined; {path.name} overrides")
            levels[task] = {"L2": dict(spec["L2"]), "L3": dict(spec["L3"])}
    return levels, excluded


def _kwargs_for(levels: dict, task: str, level: str) -> dict:
    return {} if level == "L1" else dict(levels[task][level])


def _build_one(
    staging: Path, task: str, kwargs: dict, *,
    dev_count: int, test_count: int, heldout_seed: int, revision: str,
    original_kwargs_fn,
) -> None:
    samples._dataset_kwargs = (
        lambda t, s, _k=kwargs, _orig=original_kwargs_fn: dict(_k)
        if t == task
        else _orig(t, s)
    )
    samples._worker_build(
        staging,
        task=task,
        dev_count=dev_count,
        test_count=test_count,
        dev_seed=samples.DEFAULT_DEV_SEED,
        heldout_seed=heldout_seed,
        revision=revision,
    )


def build(
    out_root: Path, levels: dict[str, dict[str, dict]], *,
    dev_count: int, test_count: int, min_test_count: int, force: bool,
) -> None:
    if out_root.exists():
        if not force:
            raise FileExistsError(f"{out_root} exists; pass --force to rebuild")
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    revision = samples._source_revision()
    original_kwargs_fn = samples._dataset_kwargs
    test_counts: dict[str, int] = {}   # per-task achieved heldout count
    level_seeds: dict[str, int] = {}   # per-level heldout seed
    dropped: dict[str, str] = {}
    summary: dict[str, dict] = {}
    try:
        for level in ("L1", "L2", "L3"):
            level_root = out_root / level
            heldout_seed = level_seeds.setdefault(level, secrets.randbits(63))
            with tempfile.TemporaryDirectory(prefix=f"rg_ladder_{level}_", dir=out_root) as tmp:
                staging = Path(tmp)
                for task in sorted(levels):
                    if task in dropped:
                        continue
                    kwargs = _kwargs_for(levels, task, level)
                    want = test_counts.get(task, test_count)
                    t0 = time.time()
                    try:
                        _build_one(
                            staging, task, kwargs,
                            dev_count=dev_count, test_count=want,
                            heldout_seed=heldout_seed, revision=revision,
                            original_kwargs_fn=original_kwargs_fn,
                        )
                    except RuntimeError as exc:
                        m = _COLLECTED_RE.search(str(exc))
                        got = int(m.group(1)) if m else 0
                        if got < min_test_count:
                            dropped[task] = f"{level}: only {got} unique heldout rows (< {min_test_count})"
                            print(f"DROP {task}: {dropped[task]}")
                            continue
                        print(f"note: {task} {level} heldout capped {want} -> {got}")
                        test_counts[task] = got
                        _build_one(
                            staging, task, kwargs,
                            dev_count=dev_count, test_count=got,
                            heldout_seed=heldout_seed, revision=revision,
                            original_kwargs_fn=original_kwargs_fn,
                        )
                        # Same count at every level of a task: rebuild the
                        # task in already-promoted earlier levels at the cap.
                        for earlier in ("L1", "L2", "L3"):
                            if earlier == level:
                                break
                            print(f"  rebuilding {earlier}/{task} at {got}")
                            _build_one(
                                out_root / earlier, task,
                                _kwargs_for(levels, task, earlier),
                                dev_count=dev_count, test_count=got,
                                heldout_seed=level_seeds[earlier],
                                revision=revision,
                                original_kwargs_fn=original_kwargs_fn,
                            )
                    print(f"  built {level}/{task} in {time.time() - t0:.0f}s", flush=True)
                level_root.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(staging, level_root)
        for task in dropped:  # a task dropped at ANY level is dropped everywhere
            for level in ("L1", "L2", "L3"):
                for sub in ("dev", "heldout"):
                    p = out_root / level / sub / samples.BENCHMARK / f"{task}.jsonl"
                    p.unlink(missing_ok=True)
                (out_root / level / "manifests" / samples.BENCHMARK / f"{task}.json").unlink(
                    missing_ok=True
                )
        for level in ("L1", "L2", "L3"):
            summary[level] = validate_level(
                out_root / level, levels,
                dev_count=dev_count, test_counts=test_counts,
                default_test_count=test_count, dropped=dropped,
            )
    finally:
        samples._dataset_kwargs = original_kwargs_fn

    (out_root / "build_summary.json").write_text(
        json.dumps({"summary": summary, "heldout_caps": test_counts, "dropped": dropped}, indent=1)
    )
    print(json.dumps({"heldout_caps": test_counts, "dropped": dropped}, indent=1))
    kept = len([t for t in levels if t not in dropped])
    print(f"OK: {out_root} ({kept} tasks x 3 levels; {len(dropped)} dropped)")


def validate_level(
    level_root: Path, levels: dict, *,
    dev_count: int, test_counts: dict[str, int], default_test_count: int,
    dropped: dict[str, str],
) -> dict:
    """Schema-load every file, check counts, manifest kwargs, disjointness."""
    report: dict[str, dict] = {}
    level = level_root.name
    for task in sorted(levels):
        if task in dropped:
            continue
        spec_kwargs = _kwargs_for(levels, task, level)
        manifest = json.loads(
            (level_root / "manifests" / samples.BENCHMARK / f"{task}.json").read_text()
        )
        for split_name, want in (
            ("dev", dev_count),
            ("test", test_counts.get(task, default_test_count)),
        ):
            split = manifest["splits"][split_name]
            if split["count"] != want:
                raise AssertionError(f"{level}/{task} {split_name} count {split['count']} != {want}")
            if split["dataset_kwargs"] != spec_kwargs:
                raise AssertionError(
                    f"{level}/{task} {split_name} manifest kwargs {split['dataset_kwargs']} "
                    f"!= spec {spec_kwargs}"
                )
        dev_rows = load_jsonl(level_root / "dev" / samples.BENCHMARK / f"{task}.jsonl")
        held_rows = load_jsonl(level_root / "heldout" / samples.BENCHMARK / f"{task}.jsonl")
        if {s.provenance["input_sha256"] for s in dev_rows} & {
            s.provenance["input_sha256"] for s in held_rows
        }:
            raise AssertionError(f"{level}/{task}: dev/heldout overlap")
        report[task] = {
            "dev": len(dev_rows),
            "heldout": len(held_rows),
            "kwargs": spec_kwargs,
            "mean_dev_question_chars": round(
                sum(len(s.input["text"]) for s in dev_rows) / len(dev_rows)
            ),
        }
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "data_difficulty")
    ap.add_argument("--levels-json", type=Path, nargs="*", default=[])
    ap.add_argument("--dev-count", type=int, default=25)
    ap.add_argument("--test-count", type=int, default=75)
    ap.add_argument("--min-test-count", type=int, default=40)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    levels, excluded = load_levels(args.levels_json)
    if excluded:
        print("excluded by knob survey:", json.dumps(excluded, indent=1))
    build(
        args.out, levels,
        dev_count=args.dev_count, test_count=args.test_count,
        min_test_count=args.min_test_count, force=args.force,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
