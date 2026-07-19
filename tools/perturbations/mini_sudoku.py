"""Perturbation module: mini_sudoku.

Original template: "In 4x4 Mini Sudoku:\n<3 rule lines>\nSolve this 4x4
Mini Sudoku puzzle:\n<grid>\nFormat your response as the puzzle above,
with spaces separating each number within a row, and newlines separating
rows.\n" (note the trailing newline). The grid is metadata `puzzle`
rendered with "_" for empty cells; verified byte-equal across L1-L3
dev+heldout (always 4x4; L1-L3 differ only in num_empty). The three rule
lines and the format directive are preserved verbatim in every variant;
only the header line and the puzzle lead-in change. The grid block is
re-emitted byte-verbatim.
"""
from __future__ import annotations

K = 3

_RULES = (
    "- Each row must contain each number from 1-4 exactly once\n"
    "- Each column must contain each number 1-4 exactly once\n"
    "- Each 2x2 subgrid must contain each number 1-4 exactly once"
)
_PREFIXES = (
    f"In 4x4 Mini Sudoku:\n{_RULES}\nSolve this 4x4 Mini Sudoku puzzle:\n",
    ("The rules of 4x4 Mini Sudoku:\n"
     f"{_RULES}\nNow solve this 4x4 Mini Sudoku puzzle:\n"),
    ("In the game of 4x4 Mini Sudoku:\n"
     f"{_RULES}\nFill in this 4x4 Mini Sudoku puzzle:\n"),
)
_SUFFIX = ("\nFormat your response as the puzzle above, with spaces "
           "separating each number within a row, and newlines separating "
           "rows.\n")


def _grid_str(puzzle):
    return "\n".join(" ".join(str(x) if x else "_" for x in row)
                     for row in puzzle)


def fields(entry):
    grid = _grid_str(entry["metadata"]["puzzle"])
    if entry["question"] != _PREFIXES[0] + grid + _SUFFIX:
        raise ValueError("mini_sudoku question != canonical template")
    return {"grid": grid}


def render(f, v):
    return _PREFIXES[v] + f["grid"] + _SUFFIX


def parse(text):
    if not text.endswith(_SUFFIX):
        raise ValueError("mini_sudoku format directive missing")
    body = text[:-len(_SUFFIX)]
    for pre in _PREFIXES:
        if body.startswith(pre):
            return {"grid": body[len(pre):]}
    raise ValueError("no mini_sudoku pattern")
