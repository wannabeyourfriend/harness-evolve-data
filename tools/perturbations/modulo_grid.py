"""Perturbation module: modulo_grid.

Original template: a fixed two-sentence head ("Identify the mathematical
pattern which defines this grid, then use that pattern to fill in the
question marks. Return the entire completed grid as your answer.\n\n")
followed by the emoji grid (lines of X/check/question-mark emoji, no
trailing newline) — identical across L1-L3 dev+heldout (levels differ
only in hole count). The answer directive sentence ("Return the entire
completed grid as your answer.") is preserved verbatim in every variant;
only the pattern-finding sentence is rephrased. The emoji grid is
re-emitted byte-verbatim. target/divisor/operation metadata (the hidden
pattern) is never read or leaked.
"""
from __future__ import annotations

K = 3

_DIRECTIVE = "Return the entire completed grid as your answer."

_HEADS = (
    ("Identify the mathematical pattern which defines this grid, then use "
     f"that pattern to fill in the question marks. {_DIRECTIVE}\n\n"),
    ("Work out the mathematical rule that generates the grid below, then "
     f"apply that rule to fill in the question marks. {_DIRECTIVE}\n\n"),
    ("The grid below follows a hidden mathematical pattern. Determine the "
     f"pattern and use it to fill in the question marks. {_DIRECTIVE}\n\n"),
)


def fields(entry):
    q = entry["question"]
    if not q.startswith(_HEADS[0]):
        raise ValueError("modulo_grid canonical head missing")
    grid = q[len(_HEADS[0]):]
    if "❔" not in grid:
        raise ValueError("modulo_grid grid has no question-mark cells")
    return {"grid": grid}


def render(f, v):
    return _HEADS[v] + f["grid"]


def parse(text):
    for head in _HEADS:
        if text.startswith(head):
            return {"grid": text[len(head):]}
    raise ValueError("no modulo_grid pattern")
