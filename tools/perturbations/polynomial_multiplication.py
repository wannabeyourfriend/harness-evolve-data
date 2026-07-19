"""Perturbation module: polynomial_multiplication.

Two canonical lead-ins appear in the data (audited dev+heldout, 100/100):
    "Calculate the following: <expr>\n<guidelines>"   (53 rows)
    "Simplify this expression: <expr>\n<guidelines>"  (47 rows)
The guidelines block ("When performing calculations, please follow these
guidelines: ...") is instruction text and is preserved verbatim in every
variant; the lead-in directive is also kept verbatim (variants only change
layout/framing around it). The polynomial expression appears byte-identical
in every variant — never transformed.
"""
from __future__ import annotations

import re

K = 3
_TAIL_MARK = "When performing calculations, please follow these guidelines:"
_LEADS = ("Calculate the following: ", "Simplify this expression: ")
_FRAME2 = "Here is your problem.\n"


def _split_tail(q: str):
    idx = q.find(_TAIL_MARK)
    if idx < 0:
        raise ValueError("polynomial_multiplication guidelines block missing")
    return q[:idx], q[idx:]


def _derive_vars(expr: str):
    return tuple(sorted(set(re.findall(r"[a-zA-Z]", expr))))


def fields(entry):
    expr = entry["metadata"]["polynomial_expr"]
    q = entry["question"]
    if expr not in q:
        raise ValueError("metadata polynomial_expr not in question")
    head, tail = _split_tail(q)
    for lead in _LEADS:
        if head == f"{lead}{expr}\n":
            break
    else:
        raise ValueError("unrecognized polynomial_multiplication lead-in")
    variables = tuple(sorted(set(entry["metadata"]["variables"])))
    if variables != _derive_vars(expr):
        raise ValueError("metadata variables do not match expression")
    return {"lead": lead, "expr": expr, "variables": variables, "tail": tail}


def render(f, v):
    if v == 0:
        return f"{f['lead']}{f['expr']}\n{f['tail']}"
    if v == 1:
        return f"{f['lead'].rstrip(' ')}\n\n{f['expr']}\n\n{f['tail']}"
    return f"{_FRAME2}{f['lead']}{f['expr']}\n{f['tail']}"


def parse(text):
    head, tail = _split_tail(text)
    if head.startswith(_FRAME2):  # v2: framing line, then the v0 layout
        head = head[len(_FRAME2):]
    for lead in _LEADS:
        bare = lead.rstrip(" ")
        if head.startswith(f"{bare}\n\n") and head.endswith("\n\n"):  # v1
            expr = head[len(bare) + 2 : -2]
            break
        if head.startswith(lead) and head.endswith("\n"):  # v0 / v2
            expr = head[len(lead) : -1]
            break
    else:
        raise ValueError("no polynomial_multiplication pattern")
    return {"lead": lead, "expr": expr, "variables": _derive_vars(expr),
            "tail": tail}
