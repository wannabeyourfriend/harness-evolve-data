"""Perturbation module: leg_counting.

Single fixed template across L1/L2/L3, dev+heldout (verified 600 rows):
"Your task is to count how many legs there are in total when given a list of
animals.\n\nNow, how many legs are there in total if you have <list>?\n"
where <list> = "{count} {noun}" items joined by ", ". Nouns keep the source's
naive plural (key + "s": "sheeps", "praying mantiss", "leechs", ...) and are
singular when count == 1; nouns may contain spaces ("praying mantis",
"sea slug") but never commas. Counts run 1..64 (L3). Metadata `animals` maps
singular name -> count (order differs from the question, so surface order is
recovered from the question and multiset-checked against metadata);
`total_legs` is never read.

Variants: v1 spells the counts as number words (nouns byte-identical:
"eight shrimps", never "eight shrimp"); v2 rephrases the asking shell to
"Given that you have <list>, how many legs are there in total?" with digits.
"""
from __future__ import annotations

import re

from runs._drivers.perturbations._common import int_to_words, words_to_ints

K = 3

_PRE = ("Your task is to count how many legs there are in total when given a "
        "list of animals.\n\n")
_Q0_HEAD = "Now, how many legs are there in total if you have "
_Q0_TAIL = "?\n"
_V2_HEAD = "Given that you have "
_V2_TAIL = ", how many legs are there in total?\n"
_DIGIT_ITEM = re.compile(r"^(\d+) (.+)$")
_WORD_ITEM = re.compile(r"^([a-z]+(?:-[a-z]+)?) (.+)$")


def fields(entry):
    q = entry["question"]
    f = parse(q)
    animals = entry["metadata"]["animals"]
    expected = sorted(
        (name if count == 1 else name + "s", count)
        for name, count in animals.items()
    )
    if sorted((noun, c) for c, noun in f["items"]) != expected:
        raise ValueError("metadata animals do not match question list")
    if render(f, 0) != q:
        raise ValueError("legs v0 does not reproduce the original question")
    return f


def render(f, v):
    if v == 1:
        lst = ", ".join(f"{int_to_words(c)} {noun}" for c, noun in f["items"])
    else:
        lst = ", ".join(f"{c} {noun}" for c, noun in f["items"])
    if v == 2:
        return f"{_PRE}{_V2_HEAD}{lst}{_V2_TAIL}"
    return f"{_PRE}{_Q0_HEAD}{lst}{_Q0_TAIL}"


def _parse_item(item):
    m = _DIGIT_ITEM.match(item)
    if m:
        return int(m.group(1)), m.group(2)
    m = _WORD_ITEM.match(item)
    if m:
        vals = words_to_ints(m.group(1))
        if len(vals) == 1:
            return vals[0], m.group(2)
    raise ValueError(f"unparseable animal item: {item!r}")


def parse(text):
    if not text.startswith(_PRE):
        raise ValueError("legs preamble missing")
    rest = text[len(_PRE):]
    if rest.startswith(_Q0_HEAD) and rest.endswith(_Q0_TAIL):
        lst = rest[len(_Q0_HEAD): len(rest) - len(_Q0_TAIL)]
    elif rest.startswith(_V2_HEAD) and rest.endswith(_V2_TAIL):
        lst = rest[len(_V2_HEAD): len(rest) - len(_V2_TAIL)]
    else:
        raise ValueError("no legs question shell pattern")
    items = tuple(_parse_item(it) for it in lst.split(", "))
    if not items:
        raise ValueError("empty animal list")
    return {"items": items}
