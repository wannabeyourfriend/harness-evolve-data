"""Apply all per-task perturbation modules -> data_fmt_tier2/benchmarks.

Discovers every task module in this package (any .py not starting with '_'),
re-runs the full round-trip selftest for each, then rewrites the task's
dev/heldout JSONLs in a copy of data/benchmarks. Usage:

    python -m runs._drivers.perturbations.build [--check]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from runs._drivers.perturbations._common import SRC, apply_rows, load_task_module, selftest

DST = SRC.parents[1] / "data_fmt_tier2" / "benchmarks"
PKG_DIR = Path(__file__).resolve().parent
TASKS = sorted(p.stem for p in PKG_DIR.glob("*.py") if not p.stem.startswith(("_", "build")))


def main(check_only=False):
    failed = [t for t in TASKS if selftest(t) != 0]
    if failed:
        print(f"SELFTEST FAILURES: {failed} — aborting build")
        return 1
    if check_only:
        print(f"check-only: {len(TASKS)} modules verified: {TASKS}")
        return 0
    if DST.parent.exists():
        shutil.rmtree(DST.parent)
    shutil.copytree(SRC, DST)
    stats = {}
    for task in TASKS:
        mod = load_task_module(task)
        for split in ("dev", "heldout"):
            src_path = SRC / split / "reasoning_gym" / f"{task}.jsonl"
            if not src_path.exists():
                continue
            rows = [json.loads(l) for l in src_path.read_text().splitlines() if l.strip()]
            rows, fellback = apply_rows(mod, rows)
            for i, v, why in fellback:
                print(f"  fallback {task}/{split}[{i}] v{v}: {why}")
            stats[f"{task}/{split}"] = {"n": len(rows), "fellback": len(fellback)}
            out = DST / split / "reasoning_gym" / f"{task}.jsonl"
            out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    total = sum(s["n"] for s in stats.values())
    fell = sum(s["fellback"] for s in stats.values())
    print(json.dumps(stats, indent=1))
    print(f"TOTAL items={total} fallbacks={fell}")
    return 0


if __name__ == "__main__":
    sys.exit(main(check_only="--check" in sys.argv))
