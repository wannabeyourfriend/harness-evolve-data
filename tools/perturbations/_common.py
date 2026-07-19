"""Shared contract + helpers for per-task perturbation modules.

Each task module (runs/_drivers/perturbations/<task>.py) must define:
    K: int                      # number of variants incl. v0
    def fields(entry) -> dict   # canonical fields from entry metadata (raise
                                # ValueError, with a sanity check that a key
                                # field literally appears in entry["question"])
    def render(f, v) -> str     # variant v surface; v0 = canonical template
    def parse(text) -> dict     # recover fields from ANY rendered variant

Contract (same as build_fmt_tier1 / PR #42):
  * parse(render(fields(e), v)) == fields(e) for every v — verified per item
  * answers / ids / order untouched; answer-format instruction sentences
    preserved verbatim (never drop a directive; never add one the original
    lacks — audit 2026-07-17)
  * verify failures fall back to the original question; items are never
    dropped
"""
from __future__ import annotations

import importlib
import json
import os
import re  # noqa: F401  (modules use it via `from _common import *` style)
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))
from harness_evolve.benchmarks.schema import input_sha256  # noqa: E402
from harness_evolve_pipeline.format_variants import (  # noqa: E402,F401
    int_to_words,
    words_to_ints,
)

# Source dataset root; override with HE_FMT_SRC to run the same modules
# against derived roots (e.g. data_difficulty/L2). Selftests must pass on
# EVERY root a build will consume.
SRC = Path(os.environ.get("HE_FMT_SRC", str(_ROOT / "data/benchmarks")))


def load_task_module(task: str):
    return importlib.import_module(f"runs._drivers.perturbations.{task}")


def verify(mod, entry, v):
    try:
        f = mod.fields(entry)
        text = mod.render(f, v)
        if mod.parse(text) != f:
            return False, "round-trip mismatch"
        if v != 0 and text == entry["question"]:
            return False, "variant identical to original"
        return True, "ok"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def apply_rows(mod, rows):
    """Rewrite TaskSample rows in place with rotated verified variants."""
    fellback = []
    for i, row in enumerate(rows):
        entry = row["oracle"]["payload"]["entry"]
        v = i % mod.K
        ok, why = verify(mod, entry, v)
        if ok and v != 0:
            entry["question"] = mod.render(mod.fields(entry), v)
            entry.setdefault("metadata", {})["format_variant"] = v
        else:
            if v != 0:
                fellback.append((i, v, why))
            entry.setdefault("metadata", {})["format_variant"] = 0
        if isinstance(row.get("input"), dict) and row["input"].get("text"):
            row["input"]["text"] = entry["question"]
            if isinstance(row.get("provenance"), dict) and "input_sha256" in row["provenance"]:
                row["provenance"]["input_sha256"] = input_sha256(entry["question"])
    return rows, fellback


def selftest(task: str) -> int:
    """Round-trip a task module against ALL real dev+heldout rows.
    Usage: python -m runs._drivers.perturbations._common <task>"""
    mod = load_task_module(task)
    total = bad = 0
    for split in ("dev", "heldout"):
        path = SRC / split / "reasoning_gym" / f"{task}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        for i, row in enumerate(rows):
            entry = row["oracle"]["payload"]["entry"]
            for v in range(mod.K):
                total += 1
                ok, why = verify(mod, entry, v)
                if not ok:
                    bad += 1
                    if bad <= 5:
                        print(f"FAIL {task}/{split}[{i}] v{v}: {why}")
    print(f"[{task}] round-trips: {total - bad}/{total} pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest(sys.argv[1]))
