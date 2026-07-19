"""Perturbation module: jugs.

Single fixed template across L1/L2/L3, dev+heldout (verified 600 rows):
bomb-story preamble + move-syntax instructions (kept byte-identical — the
'fill A' / 'pour A->B' syntax is load-bearing), then
"The empty jugs hold this many litres of water: A:{a}, B:{b}, C:{c}\n
And your target is: {t} litres.\n\nHow do you defuse the bomb?\n\n" and the
JSON answer directive (verbatim in every variant, incl. trailing newline).
Always exactly 3 jugs (A, B, C); the template says "litres" even for 1.

Metadata `puzzle.jug_capacities` + `puzzle.target` are the fields (checked to
appear literally in the question); `min_moves` is never read. Variants
rephrase the capacity/target lines and the asking sentence (v1) or reorder
target before capacities (v2).
"""
from __future__ import annotations

import re

K = 3

_PRE = (
    "You are a police officer. A maniac has planted a bomb next to a public "
    "fountain.\n\n"
    "To defuse the bomb, you must solve a puzzle. The puzzle is solved when "
    "you fill any of the available jugs with the target amount of water.\n\n"
    "You have three move types: 'fill', 'empty' and 'pour'.\n\n"
    "To fill Jug A, you 'fill A'.\n"
    "To empty Jug B, you 'empty B'.\n"
    "To pour the contents of Jug A into Jug B, you 'pour A->B'.\n"
    "All jugs are empty to begin with.\n\n"
)
_DIRECTIVE = ("Reply as a JSON-parsable list of moves which result in any of "
              "the jugs being filled with the target amount.\n")

_MIDS = [
    ("The empty jugs hold this many litres of water: A:{a}, B:{b}, C:{c}\n"
     "And your target is: {t} litres.\n\nHow do you defuse the bomb?\n\n"),
    ("The capacities of the empty jugs in litres are: A:{a}, B:{b}, C:{c}\n"
     "Your target is: {t} litres.\n\nWhat moves do you make to defuse the "
     "bomb?\n\n"),
    ("Your target is: {t} litres.\n"
     "The empty jugs hold this many litres of water: A:{a}, B:{b}, C:{c}"
     "\n\nHow do you defuse the bomb?\n\n"),
]
_MID_RES = [
    re.compile(
        "^"
        + re.escape(m)
        .replace(re.escape("{a}"), r"(?P<a>\d+)")
        .replace(re.escape("{b}"), r"(?P<b>\d+)")
        .replace(re.escape("{c}"), r"(?P<c>\d+)")
        .replace(re.escape("{t}"), r"(?P<t>\d+)")
        + "$"
    )
    for m in _MIDS
]


def fields(entry):
    md = entry["metadata"]["puzzle"]
    caps = tuple(md["jug_capacities"])
    if len(caps) != 3:
        raise ValueError("expected exactly 3 jugs")
    f = {"caps": caps, "target": int(md["target"])}
    q = entry["question"]
    capstr = f"A:{caps[0]}, B:{caps[1]}, C:{caps[2]}"
    if capstr not in q or f"your target is: {f['target']} litres" not in q:
        raise ValueError("metadata capacities/target not in question")
    if render(f, 0) != q:
        raise ValueError("jugs v0 does not reproduce the original question")
    return f


def render(f, v):
    a, b, c = f["caps"]
    return _PRE + _MIDS[v].format(a=a, b=b, c=c, t=f["target"]) + _DIRECTIVE


def parse(text):
    if not text.startswith(_PRE):
        raise ValueError("jugs preamble missing")
    if not text.endswith(_DIRECTIVE):
        raise ValueError("jugs answer directive missing")
    mid = text[len(_PRE): len(text) - len(_DIRECTIVE)]
    for pat in _MID_RES:
        m = pat.match(mid)
        if m:
            return {"caps": (int(m["a"]), int(m["b"]), int(m["c"])),
                    "target": int(m["t"])}
    raise ValueError("no jugs capacity/target pattern")
