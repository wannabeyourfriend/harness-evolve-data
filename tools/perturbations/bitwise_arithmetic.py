"""Perturbation module: bitwise_arithmetic.

Original template: a fixed one-line instruction preamble ("Please solve this
problem. Assume there is arbitrary bit depth ... Reply only with the final
hexidecimal value.") + "\n" + the parenthesized hex expression — metadata
carries `problem`. The instruction preamble is preserved verbatim in every
variant; the expression stays byte-identical (never converted to words).
"""
from __future__ import annotations

import re

K = 3
_INSTR_MARK = "Reply only with the final hexidecimal value."


def fields(entry):
    prob = entry["metadata"]["problem"]
    q = entry["question"]
    if "\n" in prob or not q.endswith("\n" + prob):
        raise ValueError("metadata problem not the last line of question")
    instr = q[: -(len(prob) + 1)]
    if _INSTR_MARK not in instr or "\n" in instr:
        raise ValueError("bitwise instruction preamble malformed")
    return {"instr": instr, "problem": prob}


def render(f, v):
    if v == 0:
        return f"{f['instr']}\n{f['problem']}"
    if v == 1:
        return f"Evaluate:\n{f['problem']}\n{f['instr']}"
    return f"{f['instr']}\nexpression = {f['problem']}"


def parse(text):
    m = re.fullmatch(r"Evaluate:\n(.+)\n(.+)", text)
    if m:
        return {"instr": m.group(2), "problem": m.group(1)}
    m = re.fullmatch(r"(.+)\nexpression = (.+)", text)
    if m:
        return {"instr": m.group(1), "problem": m.group(2)}
    m = re.fullmatch(r"(.+)\n(.+)", text)
    if m:
        return {"instr": m.group(1), "problem": m.group(2)}
    raise ValueError("no bitwise_arithmetic pattern")
