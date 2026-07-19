"""Perturbation module: propositional_logic.

Ported from the verified spec in the fmtpr worktree
(harness_evolve/benchmarks/format_variants.py, K=3). Vary only the premise
notation; the FORMAT INSTRUCTIONS block (answer notation) stays verbatim,
with one added NOTE sentence telling the solver the premises use an
alternate notation — the note is part of the variant surface and is what
parse keys on. Token maps are collision-free and exactly invertible on the
premise block (scanned: no pre-existing connective words / ASCII tokens in
any L1/L2/L3 premise block).

Deviation from the metadata route: fields are the question split around the
"Here is the question:\n" marker (as in the prior art), not the metadata
premises list — the question's numbered premise layout (".2. ..." lines) is
preserved exactly that way.
"""
from __future__ import annotations

K = 3

_MAPS = {
    1: [("∧", " AND "), ("∨", " OR "), ("→", " IMPLIES "), ("↔", " IFF "), ("¬", "NOT ")],
    2: [("∧", " & "), ("∨", " | "), ("→", " -> "), ("↔", " <-> "), ("¬", "!")],
}
_NOTES = {
    1: "NOTE: the premises below are written with word connectives (AND, OR, IMPLIES, IFF, NOT); your final answer must still use the symbol notation above.\n",
    2: "NOTE: the premises below are written with ASCII connectives (&, |, ->, <->, !); your final answer must still use the symbol notation above.\n",
}
_SPLIT = "Here is the question:\n"


def fields(entry):
    q = entry["question"]
    if _SPLIT not in q:
        raise ValueError("unexpected prop_logic layout")
    pre, prem = q.split(_SPLIT, 1)
    return {"pre": pre, "prem": prem}


def render(f, v):
    if v == 0:
        return f["pre"] + _SPLIT + f["prem"]
    prem = f["prem"]
    for sym, rep in _MAPS[v]:
        prem = prem.replace(sym, rep)
    return f["pre"] + _NOTES[v] + _SPLIT + prem


def parse(text):
    for v in (1, 2):
        note = _NOTES[v]
        if note in text:
            pre, rest = text.split(note, 1)
            if not rest.startswith(_SPLIT):
                raise ValueError("prop_logic note/split mismatch")
            prem = rest[len(_SPLIT):]
            for sym, rep in reversed(_MAPS[v]):
                prem = prem.replace(rep, sym)
            return {"pre": pre, "prem": prem}
    pre, prem = text.split(_SPLIT, 1)
    return {"pre": pre, "prem": prem}
