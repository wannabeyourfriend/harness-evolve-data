"""Apply all per-task perturbation modules to the difficulty ladder.

data_difficulty/L{1,2,3} -> data_difficulty_fmt/L{1,2,3}: every task that has
a module in this package gets rotated exact-reversible format variants
(i % K, v0 = original, fallback-never-drop); dev AND heldout are rewritten;
row provenance input_sha256 and the manifests' file sha256 are recomputed,
and each manifest gains a "format_varied" marker. Tasks present in a level
but lacking a module are copied unvaried and reported.

Selftests for every (module, level) gate the build: a module that cannot
round-trip 100% on a level's real rows aborts before anything is written.

Usage:
    python -m runs._drivers.perturbations.build_difficulty_fmt \
        [--src data_difficulty] [--dst data_difficulty_fmt] [--check]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from runs._drivers.perturbations import _common
from runs._drivers.perturbations._common import apply_rows, load_task_module

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))
from harness_evolve.benchmarks.schema import file_sha256  # noqa: E402

PKG_DIR = Path(__file__).resolve().parent
MODULE_TASKS = sorted(
    p.stem for p in PKG_DIR.glob("*.py") if not p.stem.startswith(("_", "build"))
)
LEVELS = ("L1", "L2", "L3")


def level_tasks(src: Path, level: str) -> list[str]:
    return sorted(p.stem for p in (src / level / "dev" / "reasoning_gym").glob("*.jsonl"))


def run_selftests(src: Path, tasks: list[str]) -> list[str]:
    """Run each (task, level) selftest in a subprocess (honors HE_FMT_SRC)."""
    failures = []
    for level in LEVELS:
        env = dict(os.environ, HE_FMT_SRC=str(src / level))
        for task in tasks:
            proc = subprocess.run(
                [sys.executable, "-m", "runs._drivers.perturbations._common", task],
                env=env, capture_output=True, text=True, cwd=str(_ROOT),
            )
            if proc.returncode != 0:
                failures.append(f"{level}/{task}")
                print(f"SELFTEST FAIL {level}/{task}:\n{proc.stdout[-500:]}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=_ROOT / "data_difficulty")
    ap.add_argument("--dst", type=Path, default=_ROOT / "data_difficulty_fmt")
    ap.add_argument("--check", action="store_true", help="selftests only, no build")
    args = ap.parse_args()

    all_level_tasks = {lvl: level_tasks(args.src, lvl) for lvl in LEVELS}
    present = sorted(set().union(*all_level_tasks.values()))
    covered = [t for t in present if t in MODULE_TASKS]
    uncovered = [t for t in present if t not in MODULE_TASKS]
    print(f"tasks in ladder: {len(present)}; with modules: {len(covered)}; "
          f"unvaried: {uncovered or 'none'}")

    failures = run_selftests(args.src, covered)
    if failures:
        print(f"ABORT: selftest failures: {failures}")
        return 1
    if args.check:
        print("check-only: all selftests pass")
        return 0

    if args.dst.exists():
        shutil.rmtree(args.dst)
    stats: dict[str, dict] = {}
    total_fallbacks = 0
    for level in LEVELS:
        shutil.copytree(args.src / level, args.dst / level)
        # Point the modules' selftest-root at this level for any module that
        # consults _common.SRC at runtime (none should, but keep it honest).
        _common.SRC = args.src / level
        for task in all_level_tasks[level]:
            if task not in MODULE_TASKS:
                continue
            mod = load_task_module(task)
            manifest_path = args.dst / level / "manifests" / "reasoning_gym" / f"{task}.json"
            manifest = json.loads(manifest_path.read_text())
            for split, mdir in (("dev", "dev"), ("test", "heldout")):
                path = args.dst / level / mdir / "reasoning_gym" / f"{task}.jsonl"
                rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
                rows, fellback = apply_rows(mod, rows)
                for i, v, why in fellback:
                    print(f"  fallback {level}/{task}/{split}[{i}] v{v}: {why}")
                total_fallbacks += len(fellback)
                path.write_text(
                    "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
                )
                manifest["splits"][split]["sha256"] = file_sha256(path)
                stats[f"{level}/{task}/{split}"] = {
                    "n": len(rows), "fellback": len(fellback), "K": mod.K,
                }
            manifest["format_varied"] = {
                "mechanism": "runs/_drivers/perturbations (exact-reversible, i%K rotation, v0=original)",
                "K": mod.K,
            }
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    total = sum(s["n"] for s in stats.values())
    print(f"TOTAL rows={total} fallbacks={total_fallbacks}")
    (args.dst / "fmt_build_stats.json").write_text(json.dumps(stats, indent=1))
    print(f"OK: {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
