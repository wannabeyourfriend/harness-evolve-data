"""Perturbation module: tower_of_hanoi.

Ported from the verified spec in the fmtpr worktree
(harness_evolve/benchmarks/format_variants.py, K=4). Fields come from
metadata (num_disks/num_pegs/start_peg/target_peg) with a sanity check that
they literally appear in the question. The rules block and the formatting
guidelines (answer-format directives) are preserved verbatim in every
variant; render(f, 0) reproduces the original template exactly (verified
byte-identical on all L1/L2/L3 dev+heldout rows).
"""
from __future__ import annotations

import re

from runs._drivers.perturbations._common import int_to_words, words_to_ints

K = 4

_RULES = (
    "- Only one disk can be moved at a time.\n"
    "- A larger disk cannot be placed on top of a smaller disk.\n"
    "- All disks must be on a peg at all times.\n"
)
_FMT = (
    "Formatting guidelines:\n"
    "- Each instruction should be placed on a single line.\n"
    "- Each line should be formatted as 'Move disk X from Peg Y to Peg Z'\n"
    "- Do not include any other text or formatting.\n"
)


def fields(entry):
    md = entry["metadata"]
    f = {"d": md["num_disks"], "p": md["num_pegs"],
         "src": md["start_peg"], "tgt": md["target_peg"]}
    q = entry["question"]
    if (f"with {f['d']} disks and {f['p']} pegs" not in q
            or f"from Peg {f['src']} to Peg {f['tgt']}" not in q):
        raise ValueError("metadata disks/pegs/src/tgt not in question")
    return f


def render(f, v):
    if v == 0:
        return (
            f"Solve the Tower of Hanoi problem with {f['d']} disks and {f['p']} pegs.\n"
            f"Move all disks from Peg {f['src']} to Peg {f['tgt']} following the rules:\n"
            f"{_RULES}\nProvide the sequence of moves.\n\n{_FMT}"
        )
    if v == 1:
        return (
            f"You are given a Tower of Hanoi puzzle that has {int_to_words(f['d'])} disks "
            f"stacked on {int_to_words(f['p'])} pegs.\n"
            f"Transfer the entire stack away from Peg {f['src']} so it ends up on Peg {f['tgt']}, "
            f"obeying these rules:\n{_RULES}\nProvide the sequence of moves.\n\n{_FMT}"
        )
    if v == 2:
        return (
            f"Tower of Hanoi instance: disks={f['d']}, pegs={f['p']}, "
            f"source_peg={f['src']}, target_peg={f['tgt']}.\n"
            f"Move every disk from the source peg to the target peg following the rules:\n"
            f"{_RULES}\nProvide the sequence of moves.\n\n{_FMT}"
        )
    return (
        f"Your goal is to move all disks onto Peg {f['tgt']}; they currently sit on Peg {f['src']}.\n"
        f"This Tower of Hanoi puzzle uses {f['p']} pegs and {f['d']} disks in total.\n"
        f"Follow the rules:\n{_RULES}\nProvide the sequence of moves.\n\n{_FMT}"
    )


_PATS = [
    r"with (?P<d>\d+) disks and (?P<p>\d+) pegs.*?from Peg (?P<s>\d+) to Peg (?P<t>\d+)",
    r"has (?P<dw>[a-z\- ]+?) disks stacked on (?P<pw>[a-z\- ]+?) pegs.*?away from Peg (?P<s>\d+) so it ends up on Peg (?P<t>\d+)",
    r"disks=(?P<d>\d+), pegs=(?P<p>\d+), source_peg=(?P<s>\d+), target_peg=(?P<t>\d+)",
    r"onto Peg (?P<t>\d+); they currently sit on Peg (?P<s>\d+).*?uses (?P<p>\d+) pegs and (?P<d>\d+) disks",
]


def parse(text):
    for pat in _PATS:
        m = re.search(pat, text, re.S)
        if m:
            g = m.groupdict()
            d = int(g["d"]) if g.get("d") else words_to_ints(g["dw"])[0]
            p = int(g["p"]) if g.get("p") else words_to_ints(g["pw"])[0]
            return {"d": d, "p": p, "src": int(g["s"]), "tgt": int(g["t"])}
    raise ValueError("no hanoi pattern matched")
