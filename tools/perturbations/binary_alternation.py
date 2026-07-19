"""Perturbation module: binary_alternation.

Original template (audited dev+heldout, 100/100 canonical, identical for
solvable and unsolvable rows): a fixed three-paragraph preamble (problem
statement incl. the "-1 if impossible" rule, definition of alternating,
any-two-characters swap rule) followed by
    "Now, determine the minimum number of swaps to make the following
     binary string alternating: <bits>\n"
Every preamble sentence and the final directive are preserved verbatim in
every variant; only the payload layout changes. The binary string appears
byte-identical — never transformed. metadata["solvable"] never appears in
the question text, so it is not part of fields().
"""
from __future__ import annotations

import re

K = 3
_MARK = ("Now, determine the minimum number of swaps to make the following "
         "binary string alternating:")


def fields(entry):
    s = entry["metadata"]["string"]
    q = entry["question"]
    if s not in q:
        raise ValueError("metadata string not in question")
    idx = q.find(_MARK)
    if idx < 0:
        raise ValueError("binary_alternation directive missing")
    pre = q[:idx]
    if q != f"{pre}{_MARK} {s}\n" or not re.fullmatch(r"[01]+", s):
        raise ValueError("non-canonical binary_alternation question")
    return {"pre": pre, "string": s}


def render(f, v):
    pre, s = f["pre"], f["string"]
    if v == 0:
        return f"{pre}{_MARK} {s}\n"
    if v == 1:
        return f"{pre}{_MARK}\n\n{s}\n"
    return f"{pre}{_MARK}\nInput: {s}\n"


def parse(text):
    idx = text.find(_MARK)
    if idx < 0:
        raise ValueError("binary_alternation directive missing")
    pre, rest = text[:idx], text[idx + len(_MARK):]
    for lead in ("\nInput: ", "\n\n", " "):  # v2, v1, v0
        if rest.startswith(lead) and rest.endswith("\n"):
            s = rest[len(lead):-1]
            if re.fullmatch(r"[01]+", s):
                return {"pre": pre, "string": s}
    raise ValueError("no binary_alternation pattern")
