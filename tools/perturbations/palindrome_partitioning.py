"""Perturbation module: palindrome_partitioning.

Original template: a fixed instruction preamble (palindrome definition,
any-order permission, list-of-lists output format — all preserved verbatim
as `head`) followed by "Partition the following string into palindromes:
<string>\n" — metadata carries `string` (and `solution`, which is never
read or leaked). Variants rephrase only the final payload sentence.
"""
from __future__ import annotations

import re

K = 3
_MARK0 = "Partition the following string into palindromes: "
_MARK1 = "The string to partition into palindromes is: "
_MARK2 = "String: "


def fields(entry):
    s = entry["metadata"]["string"]
    q = entry["question"]
    if s not in q:
        raise ValueError("metadata string not in question")
    idx = q.find(_MARK0)
    if idx < 0:
        raise ValueError("palindrome_partitioning marker missing")
    head = q[:idx]
    if q != f"{head}{_MARK0}{s}\n":
        raise ValueError("unexpected palindrome_partitioning layout")
    return {"head": head, "string": s}


def render(f, v):
    if v == 0:
        return f"{f['head']}{_MARK0}{f['string']}\n"
    if v == 1:
        return f"{f['head']}{_MARK1}{f['string']}\n"
    return (f"{f['head']}{_MARK2}{f['string']}\n"
            f"Partition this string into palindromes.\n")


def parse(text):
    for mark, pat in (
        (_MARK0, r"([a-z]+)\n"),
        (_MARK1, r"([a-z]+)\n"),
        (_MARK2, r"([a-z]+)\nPartition this string into palindromes\.\n"),
    ):
        idx = text.find(mark)
        if idx < 0:
            continue
        m = re.fullmatch(pat, text[idx + len(mark):])
        if m:
            return {"head": text[:idx], "string": m.group(1)}
    raise ValueError("no palindrome_partitioning pattern")
