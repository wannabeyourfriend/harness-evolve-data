"""Perturbation module: polynomial_equations.

Original template: one of several head sentences ("Solve for real q: ",
"Determine the real value(s) of a that satisfies: ", "Solve the polynomial
equation for real x:\n", "Find the real value(s) of o in the equation: ")
+ "{expr} = 0" + "\n" + the long numbered answer-format instruction block
("In solving equations, please follow these instructions: 1. ... 5. ...").
Metadata carries polynomial_expr/variable. Head sentence (incl. its
space-vs-newline separator) and the full instruction block are preserved
verbatim in every variant; the expression stays byte-identical.
"""
from __future__ import annotations

K = 3
_TAIL_MARK = "In solving equations, please follow these instructions:"
_TAIL_END = "5 or greater).\n"
_V1_HEAD = "Problem:\n"
_V1_SEP = "\nInstructions:\n"


def fields(entry):
    md = entry["metadata"]
    expr, var = md["polynomial_expr"], md["variable"]
    q = entry["question"]
    ti = q.find(_TAIL_MARK)
    if ti < 0:
        raise ValueError("polynomial tail marker missing")
    tail = q[ti:]
    if not tail.endswith(_TAIL_END):
        raise ValueError("polynomial tail end marker missing")
    pre = q[:ti]
    # rfind: a degenerate expr like "w" also occurs inside the head sentence
    j = pre.rfind(expr)
    if j < 0:
        raise ValueError("metadata polynomial_expr not in question")
    head, rest = pre[:j], pre[j + len(expr):]
    if rest != " = 0\n":
        raise ValueError("equation suffix is not ' = 0'")
    if head.count(":") != 1 or head[-1] not in (" ", "\n") or head[-2] != ":":
        raise ValueError("unrecognized head sentence")
    if {c for c in expr if c.isalpha()} != {var}:
        raise ValueError("metadata variable does not match expression")
    return {"head": head, "expr": expr, "var": var, "tail": tail}


def render(f, v):
    eq = f"{f['head']}{f['expr']} = 0"
    if v == 0:
        return f"{eq}\n{f['tail']}"
    if v == 1:
        return f"{_V1_HEAD}{eq}{_V1_SEP}{f['tail']}"
    return f"{f['tail']}{eq}"  # instruction block first, equation last


def parse(text):
    if text.startswith(_TAIL_MARK):  # v2: instructions first
        cut = text.find(_TAIL_END)
        if cut < 0:
            raise ValueError("tail end marker missing")
        cut += len(_TAIL_END)
        tail, eq = text[:cut], text[cut:]
    elif text.startswith(_V1_HEAD):  # v1: labeled sections
        body = text[len(_V1_HEAD):]
        cut = body.find(_V1_SEP)
        if cut < 0:
            raise ValueError("v1 instructions marker missing")
        eq, tail = body[:cut], body[cut + len(_V1_SEP):]
    else:  # v0: canonical
        ti = text.find(_TAIL_MARK)
        if ti < 1 or text[ti - 1] != "\n":
            raise ValueError("no polynomial_equations pattern")
        eq, tail = text[:ti - 1], text[ti:]
    if not eq.endswith(" = 0"):
        raise ValueError("equation suffix missing")
    i = eq.find(":")
    if i < 0 or eq[i + 1] not in (" ", "\n"):
        raise ValueError("head separator missing")
    head, expr = eq[: i + 2], eq[i + 2: -len(" = 0")]
    letters = {c for c in expr if c.isalpha()}
    if len(letters) != 1:
        raise ValueError("cannot infer variable from expression")
    return {"head": head, "expr": expr, "var": letters.pop(), "tail": tail}
