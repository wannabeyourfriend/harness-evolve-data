"""Perturbation module: syllogism.

Original template: "Consider these statements:\n1. <premise1>\n2. <premise2>
\n\nDoes it logically follow that:\n<conclusion>?\n(Answer Yes or No)" —
metadata carries premise1/premise2/conclusion, all of which the question
itself shows (is_valid is never touched). The "Does it logically follow
that:" question and the "(Answer Yes or No)" directive are preserved
verbatim in every variant; only the header phrasing and premise layout
change. Both `type: syllogism` and `type: inversion` entries use this
same surface template (verified across dev+heldout).
"""
from __future__ import annotations

import re

K = 3

_TAIL_RE = re.compile(
    r"\n\nDoes it logically follow that:\n([^\n]+)\?\n\(Answer Yes or No\)$")


def _tail(c):
    return f"\n\nDoes it logically follow that:\n{c}?\n(Answer Yes or No)"


def fields(entry):
    md = entry["metadata"]
    f = {"premise1": md["premise1"], "premise2": md["premise2"],
         "conclusion": md["conclusion"]}
    q = entry["question"]
    if not all(s and s in q for s in f.values()):
        raise ValueError("metadata premises/conclusion not in question")
    return f


def render(f, v):
    p1, p2, c = f["premise1"], f["premise2"], f["conclusion"]
    if v == 0:
        return f"Consider these statements:\n1. {p1}\n2. {p2}" + _tail(c)
    if v == 1:
        return f"Consider the following premises:\n- {p1}\n- {p2}" + _tail(c)
    return f"Premise 1: {p1}\nPremise 2: {p2}" + _tail(c)


def parse(text):
    m = _TAIL_RE.search(text)
    if not m:
        raise ValueError("syllogism answer-directive tail missing")
    c = m.group(1)
    head = text[: m.start()]
    for pat in (r"\n1\. ([^\n]+)\n2\. ([^\n]+)$",
                r"\n- ([^\n]+)\n- ([^\n]+)$",
                r"^Premise 1: ([^\n]+)\nPremise 2: ([^\n]+)$"):
        pm = re.search(pat, head)
        if pm:
            return {"premise1": pm.group(1), "premise2": pm.group(2),
                    "conclusion": c}
    raise ValueError("no syllogism premise pattern")
