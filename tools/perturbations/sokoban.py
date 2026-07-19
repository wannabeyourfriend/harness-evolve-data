"""Perturbation module: sokoban.

Original template: a fixed opener ("You are going to solve a 'sokoban'
puzzle."), the 7-line symbol legend, the answer-format directive ("Your
solution must be a string of characters, ex: LDURRUDL."), then "Here is
your puzzle:\n<board>". The board is byte-identical to metadata
`gamestr` (rows with trailing double spaces, ending in a blank line);
verified question == prefix + gamestr across L1-L3 dev+heldout. The
legend and the directive are preserved verbatim in every variant; only
the opener sentence and the board lead-in line change. The board block
is re-emitted byte-verbatim and never reflowed.
"""
from __future__ import annotations

K = 3

_LEGEND = (
    "* - The player\n"
    "% - The player on a goal\n"
    "@ - A box\n"
    "X - A goal\n"
    "$ - A box on a goal\n"
    "+ - A wall\n"
    "- - An empty position"
)
_DIRECTIVE = "Your solution must be a string of characters, ex: LDURRUDL."

_PREFIXES = (
    ("You are going to solve a 'sokoban' puzzle.\n\n"
     f"{_LEGEND}\n\n{_DIRECTIVE}\n\nHere is your puzzle:\n"),
    ("Your task is to solve the following 'sokoban' puzzle.\n\n"
     f"{_LEGEND}\n\n{_DIRECTIVE}\n\nThe puzzle to solve is:\n"),
    ("Below is a 'sokoban' puzzle for you to solve.\n\n"
     f"{_LEGEND}\n\n{_DIRECTIVE}\n\nPuzzle grid:\n"),
)


def fields(entry):
    board = entry["metadata"]["gamestr"]
    if entry["question"] != _PREFIXES[0] + board:
        raise ValueError("sokoban question != canonical prefix + gamestr")
    return {"board": board}


def render(f, v):
    return _PREFIXES[v] + f["board"]


def parse(text):
    for pre in _PREFIXES:
        if text.startswith(pre):
            return {"board": text[len(pre):]}
    raise ValueError("no sokoban pattern")
