"""Perturbation module: basic_arithmetic.

Ported from the _mk_expr_spec metadata-route spec in
runs/_drivers/build_fmt_tier1.py: fields come from metadata["expression"]
(sanity-checked to appear literally in the question). Deviation: the ladder
originals are uniformly "Calculate {expr}." (all L1/L2/L3 dev+heldout
rows), so render(f, 0) emits that template — byte-identical to the
original — instead of tier1's "State the final answer..." canonical. The
word-form variant words only the OPERATORS (numbers stay digits, so 5-digit
L3 terms are unaffected); no answer-format directive is added or dropped
(the original carries none beyond the bare imperative).
"""
from __future__ import annotations

import re

K = 3

_OPW = {"+": "plus", "-": "minus", "*": "times", "/": "divided by"}
_WOP = {w: s for s, w in _OPW.items()}


def _expr_words(expr):
    """'3 + -4 * 5' -> '3 plus negative 4 times 5' (numbers stay digits)."""
    out = []
    for tok in expr.split():
        if tok in _OPW:
            out.append(_OPW[tok])
        elif tok.startswith("-") and len(tok) > 1:
            out.append("negative " + tok[1:])
        else:
            out.append(tok)
    return " ".join(out)


def _words_expr(text):
    out = []
    toks = text.split()
    i = 0
    while i < len(toks):
        t = toks[i]
        if t == "divided" and i + 1 < len(toks) and toks[i + 1] == "by":
            out.append("/")
            i += 2
            continue
        if t in _WOP:
            out.append(_WOP[t])
        elif t == "negative" and i + 1 < len(toks):
            out.append("-" + toks[i + 1])
            i += 1
        else:
            out.append(t)
        i += 1
    return " ".join(out)


def fields(entry):
    expr = entry["metadata"]["expression"]
    if expr not in entry["question"]:
        raise ValueError("metadata expression not in question")
    return {"expr": expr}


def render(f, v):
    if v == 0:
        return f"Calculate {f['expr']}."
    if v == 1:
        # No added answer-format directive: the original bare "Calculate X."
        # carries none, and variants must never add one (audit 2026-07-17).
        return f"Evaluate the expression written out in words: {_expr_words(f['expr'])}"
    return f"Compute the value of\n    {f['expr']}"


def parse(text):
    m = re.search(r"\ACalculate (.+)\.\Z", text)
    if m:
        return {"expr": m.group(1).strip()}
    m = re.search(r"written out in words: (.+)$", text, re.S)
    if m:
        return {"expr": _words_expr(m.group(1).strip())}
    m = re.search(r"\ACompute the value of\n    (.+)\Z", text, re.S)
    if m:
        return {"expr": m.group(1).strip()}
    raise ValueError("no expression pattern")
