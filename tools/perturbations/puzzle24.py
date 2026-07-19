"""Perturbation module: puzzle24 (exemplar for the per-task contract).

Original template: "Make 24 using 3, 1, 1, 8. You can only use each number
once. You can use the operators +, -, *, /. ..." — metadata carries `numbers`.
The operator/instruction tail is preserved verbatim in every variant.
"""
from __future__ import annotations

import re

from runs._drivers.perturbations._common import int_to_words, words_to_ints

K = 3
_TAIL_MARK = "You can only use each number once."


def _split_tail(q: str) -> str:
    idx = q.find(_TAIL_MARK)
    if idx < 0:
        raise ValueError("puzzle24 tail marker missing")
    return q[idx:]


def fields(entry):
    nums = tuple(entry["metadata"]["numbers"])
    q = entry["question"]
    if not all(str(n) in q for n in nums):
        raise ValueError("metadata numbers not in question")
    return {"nums": nums, "tail": _split_tail(q)}


def render(f, v):
    nums = ", ".join(str(n) for n in f["nums"])
    if v == 0:
        return f"Make 24 using {nums}. {f['tail']}"
    if v == 1:
        words = ", ".join(int_to_words(n) for n in f["nums"])
        return (f"Using the numbers {words}, build an expression that equals "
                f"twenty-four. {f['tail']}")
    return (f"Target: 24. Available numbers: {nums}. Construct an expression "
            f"reaching the target. {f['tail']}")


def parse(text):
    tail = _split_tail(text)
    head = text[: text.find(_TAIL_MARK)]
    m = re.search(r"Make 24 using ([0-9, ]+)\.", head)
    if m:
        return {"nums": tuple(int(x) for x in m.group(1).split(",")),
                "tail": tail}
    m = re.search(r"Using the numbers ([a-z,\- ]+), build", head)
    if m:
        nums = tuple(words_to_ints(c)[0] for c in m.group(1).split(","))
        return {"nums": nums, "tail": tail}
    m = re.search(r"Available numbers: ([0-9, ]+)\.", head)
    if m:
        return {"nums": tuple(int(x) for x in m.group(1).split(",")),
                "tail": tail}
    raise ValueError("no puzzle24 pattern")
