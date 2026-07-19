"""Perturbation module: complex_arithmetic.

Original template: "{Add|Subtract|Multiply|Divide} the complex numbers:
(a + bi) {+|-|x|/} (c + di)" — metadata carries num1/num2 (possibly wrapped
as {'__task_sample_type__': 'tuple', 'items': [...]}) and `operation`. The
head sentence is preserved verbatim; the operand literals (incl. odd forms
like "(-9.00i)") stay byte-identical inside every variant.
"""
from __future__ import annotations

import re

K = 3
_VERB = {"+": "Add", "-": "Subtract", "*": "Multiply", "/": "Divide"}
_SYM = {"+": "+", "-": "-", "*": "×", "/": "÷"}
_OP_OF_VERB = {v: k for k, v in _VERB.items()}
_V0_RE = re.compile(
    r"(Add|Subtract|Multiply|Divide) the complex numbers: "
    r"(\(.+?\)) (.) (\(.+?\))")
_V1_RE = re.compile(
    r"(Add|Subtract|Multiply|Divide) the complex numbers:\n"
    r"(\(.+?\)) (.) (\(.+?\))")
_V2_RE = re.compile(
    r"z1 = (\(.+?\))\nz2 = (\(.+?\))\n"
    r"(Add|Subtract|Multiply|Divide) the complex numbers: z1 (.) z2")


def _unwrap(x):
    if isinstance(x, dict) and "items" in x:
        return tuple(x["items"])
    return tuple(x)


def _as_complex(s):
    body = s.strip("()").replace(" ", "").replace("i", "j")
    if body.endswith("j") and body[:-1] in ("", "+", "-"):
        body = body[:-1] + "1j"
    return complex(body)


def fields(entry):
    md = entry["metadata"]
    op = md["operation"]
    q = entry["question"]
    m = _V0_RE.fullmatch(q)
    if not m or m.group(1) != _VERB[op] or m.group(3) != _SYM[op]:
        raise ValueError("complex_arithmetic head/operator mismatch")
    lhs, rhs = m.group(2), m.group(4)
    for s, n in ((lhs, _unwrap(md["num1"])), (rhs, _unwrap(md["num2"]))):
        c = _as_complex(s)
        if abs(c.real - n[0]) > 1e-6 or abs(c.imag - n[1]) > 1e-6:
            raise ValueError("operand literal does not match metadata")
    f = {"op": op, "lhs": lhs, "rhs": rhs}
    if render(f, 0) != q:
        raise ValueError("canonical render differs from question")
    return f


def render(f, v):
    head = f"{_VERB[f['op']]} the complex numbers:"
    expr = f"{f['lhs']} {_SYM[f['op']]} {f['rhs']}"
    if v == 0:
        return f"{head} {expr}"
    if v == 1:
        return f"{head}\n{expr}"
    return f"z1 = {f['lhs']}\nz2 = {f['rhs']}\n{head} z1 {_SYM[f['op']]} z2"


def parse(text):
    for pat, vi, li, ri, si in ((_V0_RE, 1, 2, 4, 3),
                                (_V1_RE, 1, 2, 4, 3),
                                (_V2_RE, 3, 1, 2, 4)):
        m = pat.fullmatch(text)
        if m:
            op = _OP_OF_VERB[m.group(vi)]
            if m.group(si) != _SYM[op]:
                raise ValueError("operator symbol/verb mismatch")
            return {"op": op, "lhs": m.group(li), "rhs": m.group(ri)}
    raise ValueError("no complex_arithmetic pattern")
