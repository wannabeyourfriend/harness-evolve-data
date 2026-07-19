"""Perturbation module: circuit_logic.

Ported from the fmtpr worktree spec (K=3) with the relabel maps EXTENDED to
the full alphabet. The prior art mapped only A-M two ways, so circuits with
more than 13 input letters legitimately fell back — but on the difficulty
ladder that would be ~45% of L2 and ~95% of L3 rows (letter counts reach 26
at L3), so the maps here are full-alphabet bijections:

  v1 = ROT13   (A->N ... M->Z, N->A ... Z->M)   — self-inverse
  v2 = Atbash  (A->Z, B->Y, ..., Z->A)          — self-inverse

Only the two anchored positions are relabeled: diagram line heads "X: ───"
and assignment lines "  X = v". The ASCII art body and the gate legend are
untouched (replacing free-standing letters would corrupt gate names like
AND/NAND). Detection is order-aware: original inputs are always consecutive
letters ascending from A (verified on all L1/L2/L3 rows), so parse inverts
whichever map restores that canonical head sequence — unambiguous for any
input count 1..26 (a ROT13'd sequence starts at N, an Atbash'd one descends
from Z; neither can imitate the canonical form or each other).
"""
from __future__ import annotations

import re

K = 3

_MAPS = {
    1: {chr(ord("A") + i): chr(ord("A") + (i + 13) % 26) for i in range(26)},  # ROT13
    2: {chr(ord("A") + i): chr(ord("Z") - i) for i in range(26)},              # Atbash
}

_HEAD_RE = re.compile(r"(?m)^([A-Z]): ")
_ASSIGN_RE = re.compile(r"(?m)^(\s*)([A-Z]) = ")


def _heads(text):
    """Diagram input letters in first-seen (top-to-bottom) order."""
    return _HEAD_RE.findall(text)


def _canonical(heads):
    """True iff heads are consecutive letters ascending from A."""
    return bool(heads) and heads == [chr(ord("A") + i) for i in range(len(heads))]


def _apply(q, mapping):
    q = _HEAD_RE.sub(lambda m: mapping.get(m.group(1), m.group(1)) + ": ", q)
    q = _ASSIGN_RE.sub(
        lambda m: m.group(1) + mapping.get(m.group(2), m.group(2)) + " = ", q)
    return q


def fields(entry):
    q = entry["question"]
    if not _heads(q):
        raise ValueError("no circuit input lines in question")
    return {"q": q}


def render(f, v):
    if v == 0:
        return f["q"]
    return _apply(f["q"], _MAPS[v])


def parse(text):
    heads = _heads(text)
    if _canonical(heads):
        return {"q": text}
    for v in (1, 2):
        inv = _MAPS[v]  # both maps are self-inverse
        if _canonical([inv.get(h, h) for h in heads]):
            return {"q": _apply(text, inv)}
    return {"q": text}
