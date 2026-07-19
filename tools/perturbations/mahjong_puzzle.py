"""Perturbation module: mahjong_puzzle.

Layout (uniform across L1/L2/L3 dev+heldout, verified 2026-07-19):
    <rules block incl. the output directive, verbatim `head`>
    "Now, given the initial cards <CARDS>, what is the result at the end of
    performing the following rounds of operations:\n"
    <"Round N: Add ... card and remove ... card.\n" lines, verbatim `body`>

The rules block is directive-like (incl. the 'Your output should be one of
the following: "Peng", "Chi", or "Pass"' sentence) and the round-history
body is machine output (up to 100 rounds at L3) — both preserved verbatim.
Variants rephrase ONLY the single lead-in sentence carrying the initial
cards. metadata `rounds`/`solution` carry per-round results and the answer;
only len(rounds) is read (sanity), nothing is leaked.
"""
from __future__ import annotations

import re

K = 3

# Lead-in templates; {c} = initial cards. Chosen so no pattern is a
# substring of another and none can occur in the fixed head or round body.
_LEADS = (
    "Now, given the initial cards {c}, what is the result at the end of "
    "performing the following rounds of operations:\n",
    "The initial cards are {c}. What is the result at the end of performing "
    "the following rounds of operations:\n",
    "Given the starting cards {c}, what is the result at the end of "
    "performing the rounds of operations below:\n",
)
_LEAD_RES = tuple(
    re.compile(re.escape(t).replace(re.escape("{c}"), "([A-Z]+)"))
    for t in _LEADS
)


def _split(text):
    for pat in _LEAD_RES:
        hits = list(pat.finditer(text))
        if not hits:
            continue
        if len(hits) != 1:
            raise ValueError("ambiguous mahjong lead-in")
        m = hits[0]
        return {"head": text[: m.start()], "cards": m.group(1),
                "body": text[m.end():]}
    raise ValueError("no mahjong_puzzle lead-in pattern")


def fields(entry):
    q = entry["question"]
    f = _split(q)
    if f["cards"] not in q:  # literal-appearance sanity (trivially true)
        raise ValueError("cards not in question")
    lines = [l for l in f["body"].splitlines() if l.strip()]
    if not all(l.startswith("Round ") for l in lines):
        raise ValueError("unexpected mahjong round body")
    rounds = entry.get("metadata", {}).get("rounds")
    if rounds is not None and len(rounds) != len(lines):
        raise ValueError("metadata rounds count != body round lines")
    if render(f, 0) != q:
        raise ValueError("mahjong_puzzle v0 reconstruction mismatch")
    return f


def render(f, v):
    return f"{f['head']}{_LEADS[v].format(c=f['cards'])}{f['body']}"


def parse(text):
    return _split(text)
