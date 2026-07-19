"""Perturbation module: sudoku.

Original template: "Solve this Sudoku puzzle:\n<grid>\nRespond with only
your answer, formatted as the puzzle, a 9x9 grid with numbers separated
by spaces, and rows separated by newlines." (no trailing newline). The
grid is metadata `puzzle` rendered with "_" for empty cells; verified
byte-equal across L1-L3 dev+heldout (always 9x9; levels differ only in
num_empty). The answer-format directive is preserved verbatim in every
variant; only the lead-in line changes. The grid block is re-emitted
byte-verbatim.
"""
from __future__ import annotations

K = 3

_PREFIXES = (
    "Solve this Sudoku puzzle:\n",
    "Here is a Sudoku puzzle for you to solve:\n",
    "Fill in the missing cells of this Sudoku puzzle:\n",
)
_SUFFIX = ("\nRespond with only your answer, formatted as the puzzle, a "
           "9x9 grid with numbers separated by spaces, and rows separated "
           "by newlines.")


def _grid_str(puzzle):
    return "\n".join(" ".join(str(x) if x else "_" for x in row)
                     for row in puzzle)


def fields(entry):
    grid = _grid_str(entry["metadata"]["puzzle"])
    if entry["question"] != _PREFIXES[0] + grid + _SUFFIX:
        raise ValueError("sudoku question != canonical template")
    return {"grid": grid}


def render(f, v):
    return _PREFIXES[v] + f["grid"] + _SUFFIX


def parse(text):
    if not text.endswith(_SUFFIX):
        raise ValueError("sudoku answer directive missing")
    body = text[:-len(_SUFFIX)]
    for pre in _PREFIXES:
        if body.startswith(pre):
            return {"grid": body[len(pre):]}
    raise ValueError("no sudoku pattern")
