"""Perturbation module: ab (A::B token-rewriting).

Layout (uniform across L1/L2/L3 dev+heldout, verified 2026-07-19):
    <rules block: token list, example program, rewrite-rule table,
     explanation — all directive-like, verbatim `head`>
    "Now, consider the following program:\n\n"
    <PROGRAM: space-separated A#/#A/B#/#B tokens, verbatim>
    "\n\nReturn the final state of the program.\n"

The rewrite-rule list and the final answer directive are kept verbatim in
every variant; the program token sequence is byte-for-byte untouched.
Variants rephrase ONLY the one framing lead-in sentence. Lead-ins are
chosen so none is a substring of another and none occurs in the fixed
rules block. metadata difficulty.length cross-checks the token count.
"""
from __future__ import annotations

K = 3

_TAIL = "\n\nReturn the final state of the program.\n"
_LEADS = (
    "Now, consider the following program:\n\n",
    "Consider this program:\n\n",
    "Here is the program:\n\n",
)
_TOKENS = ("A#", "#A", "B#", "#B")


def _split(text):
    for lead in _LEADS:
        idx = text.find(lead)
        if idx < 0:
            continue
        if text.count(lead) != 1:
            raise ValueError("ambiguous ab lead-in")
        if not text.endswith(_TAIL):
            raise ValueError("ab tail directive missing")
        program = text[idx + len(lead): -len(_TAIL)]
        if not program or not all(t in _TOKENS for t in program.split(" ")):
            raise ValueError("unexpected ab program tokens")
        return {"head": text[:idx], "program": program}
    raise ValueError("no ab lead-in pattern")


def fields(entry):
    q = entry["question"]
    f = _split(q)
    if f["program"] not in q:  # literal-appearance sanity (trivially true)
        raise ValueError("program not in question")
    length = entry.get("metadata", {}).get("difficulty", {}).get("length")
    if length is not None and len(f["program"].split(" ")) != length:
        raise ValueError("metadata difficulty.length != token count")
    if render(f, 0) != q:
        raise ValueError("ab v0 reconstruction mismatch")
    return f


def render(f, v):
    return f"{f['head']}{_LEADS[v]}{f['program']}{_TAIL}"


def parse(text):
    return _split(text)
