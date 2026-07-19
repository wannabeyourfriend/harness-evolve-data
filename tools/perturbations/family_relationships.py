"""Perturbation module: family_relationships.

Original surface: "<story sentences>\n\n<question>" where the story is a
paragraph of marriage/child sentences and the question is one of THREE native
templates (all present in L1/L2/L3, dev+heldout; verified 600 rows):
  0. "What is P1 to P2? Respond only with the word that describes their
     relationship."
  1. "What relation is P1 to P2? Answer with a single word."
  2. "How is P1 related to P2? Provide the relationship in one word."

The story block is verbatim data (byte-identical in every variant); person1 /
person2 come from metadata and are checked against the question. `qkind`
records which native template the item uses so v0 reproduces it exactly and
each variant keeps that template's answer-format directive verbatim. The
`relationship` answer in metadata is never read.

Variants: v1 prefixes the asking sentence with "In this family, " (directive
unchanged); v2 moves a lead-in line before the story and keeps the native
question ("asking sentence after a framed body" reordering).
"""
from __future__ import annotations

import re

K = 3

_NATIVE = [
    ("What is {p1} to {p2}? "
     "Respond only with the word that describes their relationship."),
    "What relation is {p1} to {p2}? Answer with a single word.",
    "How is {p1} related to {p2}? Provide the relationship in one word.",
]
_INFAMILY = [
    ("In this family, what is {p1} to {p2}? "
     "Respond only with the word that describes their relationship."),
    "In this family, what relation is {p1} to {p2}? Answer with a single word.",
    ("In this family, how is {p1} related to {p2}? "
     "Provide the relationship in one word."),
]
_V2_PREFIX = "Consider these family facts:\n"


def _q_res(templates):
    return [
        re.compile(
            "^"
            + re.escape(t)
            .replace(re.escape("{p1}"), "(.+?)")
            .replace(re.escape("{p2}"), "(.+?)")
            + "$"
        )
        for t in templates
    ]


_NATIVE_RES = _q_res(_NATIVE)
_INFAMILY_RES = _q_res(_INFAMILY)


def fields(entry):
    q = entry["question"]
    f = parse(q)
    md = entry["metadata"]
    if f["p1"] != md["person1"] or f["p2"] != md["person2"]:
        raise ValueError("metadata person1/person2 not in question tail")
    if render(f, 0) != q:
        raise ValueError("family v0 does not reproduce the original question")
    return f


def render(f, v):
    story, k = f["story"], f["qkind"]
    if v == 0:
        return f"{story}\n\n" + _NATIVE[k].format(p1=f["p1"], p2=f["p2"])
    if v == 1:
        return f"{story}\n\n" + _INFAMILY[k].format(p1=f["p1"], p2=f["p2"])
    return (f"{_V2_PREFIX}{story}\n\n"
            + _NATIVE[k].format(p1=f["p1"], p2=f["p2"]))


def parse(text):
    if text.startswith(_V2_PREFIX):
        text = text[len(_V2_PREFIX):]
    parts = text.split("\n\n")
    if len(parts) != 2:
        raise ValueError("family story/question split failed")
    story, tail = parts
    for res in (_NATIVE_RES, _INFAMILY_RES):
        for k, pat in enumerate(res):
            m = pat.match(tail)
            if m:
                return {"story": story, "p1": m.group(1), "p2": m.group(2),
                        "qkind": k}
    raise ValueError("no family question pattern")
