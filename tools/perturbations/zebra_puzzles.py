"""Perturbation module: zebra_puzzles.

Original template (uniform across L1/L2/L3, dev+heldout; verified 300 rows):
"This is a logic puzzle. There are N houses (numbered 1 on the left, N on the
right), from the perspective of someone standing across the street from them.
Each has a different person in them. They have different characteristics:\n
 - <characteristic lines>\n\n1. <clue>\n...\n\nWhat is Name of the person who
lives in House 1?? Provide only the name of the person as your final answer."

Metadata carries only difficulty counters, so the characteristic block and the
numbered clue list are treated as verbatim fields (byte-identical in every
variant). Variants rephrase only the lead-in sentence and the asking sentence;
the "Provide only the name of the person as your final answer." directive is
preserved verbatim (including the original's double "??" in v0).
"""
from __future__ import annotations

import re

K = 3

_HEADS = [
    ("This is a logic puzzle. There are {n} houses (numbered 1 on the left, "
     "{n} on the right), from the perspective of someone standing across the "
     "street from them. Each has a different person in them. They have "
     "different characteristics:\n"),
    ("Here is a logic puzzle. There are {n} houses in a row (numbered 1 on "
     "the left, {n} on the right), from the perspective of someone standing "
     "across the street from them. A different person lives in each of them. "
     "They have different characteristics:\n"),
    ("Solve this logic puzzle. There are {n} houses (numbered 1 on the left "
     "through {n} on the right), from the perspective of someone standing "
     "across the street from them. Each house is home to a different person. "
     "They have different characteristics:\n"),
]
_HEAD_RES = [
    re.compile("^" + re.escape(h).replace(re.escape("{n}"), r"(\d+)"))
    for h in _HEADS
]
_DIRECTIVE = "Provide only the name of the person as your final answer."
_TAILS = [
    f"What is Name of the person who lives in House 1?? {_DIRECTIVE}",
    f"Which name belongs to the person who lives in House 1? {_DIRECTIVE}",
    f"What is the name of the person who lives in House 1? {_DIRECTIVE}",
]


def fields(entry):
    q = entry["question"]
    f = parse(q)
    n_meta = entry["metadata"]["difficulty"]["num_people"]
    if f["n"] != n_meta:
        raise ValueError("house count does not match metadata num_people")
    if render(f, 0) != q:
        raise ValueError("zebra v0 does not reproduce the original question")
    return f


def render(f, v):
    head = _HEADS[v].format(n=f["n"])
    return f"{head}{f['chars']}\n\n{f['clues']}\n\n{_TAILS[v]}"


def parse(text):
    tail = next((t for t in _TAILS if text.endswith(t)), None)
    if tail is None:
        raise ValueError("zebra answer tail missing")
    m = next((p.match(text) for p in _HEAD_RES if p.match(text)), None)
    if m is None:
        raise ValueError("no zebra head pattern")
    if m.group(1) != m.group(2):
        raise ValueError("zebra house counts disagree")
    mid = text[m.end(): len(text) - len(tail)]
    if not mid.endswith("\n\n"):
        raise ValueError("zebra body/tail separator missing")
    blocks = mid[:-2].split("\n\n")
    if len(blocks) != 2:
        raise ValueError("zebra body is not chars + clues blocks")
    chars, clues = blocks
    if not all(l.startswith(" - ") for l in chars.split("\n")):
        raise ValueError("zebra characteristics block malformed")
    if not all(re.match(r"^\d+\. ", l) for l in clues.split("\n")):
        raise ValueError("zebra clue block malformed")
    return {"n": int(m.group(1)), "chars": chars, "clues": clues}
