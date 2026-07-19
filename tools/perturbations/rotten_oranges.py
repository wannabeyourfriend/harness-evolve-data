"""Perturbation module: rotten_oranges.

Original template: intro sentence + three-value legend + rotting rule +
task sentence (with the source's "task is determine" typo) + "If this is
impossible, return -1." directive + lead-in, then the 0/1/2 grid — metadata
carries `matrix` (matches the grid byte-for-byte) and `solution` (never read
or leaked). The grid block, the legend lines, the rotting rule and the "-1"
directive are byte-verbatim in every variant; variants rephrase only the
intro, task and lead-in sentences. Same surface at every difficulty level
(only the grid grows).
"""
from __future__ import annotations

K = 3

_LEGEND = ("- 0 representing an empty cell\n"
           "- 1 representing a fresh orange\n"
           "- 2 representing a rotten orange\n\n")
_RULE = ("Every minute, any fresh orange that is 4-directionally adjacent "
         "to a rotten orange becomes rotten.\n\n")
_IMP = "If this is impossible, return -1.\n\n"

_PREFIX = (
    # v0 — canonical reasoning_gym surface (incl. the "is determine" typo).
    ("You are given an n x n grid where each cell can have one of three "
     "values:\n" + _LEGEND + _RULE +
     "Your task is determine the minimum number of minutes that must elapse "
     "until no cell has a fresh orange.\n" + _IMP +
     "Now, determine the minimum number of minutes that must elapse until "
     "no cell in the grid below has a fresh orange:\n"),
    ("Here is an n x n grid in which each cell can take one of three "
     "values:\n" + _LEGEND + _RULE +
     "Your task is to work out the minimum number of minutes that must "
     "elapse until no cell has a fresh orange.\n" + _IMP +
     "For the grid below, determine the minimum number of minutes that must "
     "elapse until no cell has a fresh orange:\n"),
    ("Consider an n x n grid where every cell holds one of three "
     "values:\n" + _LEGEND + _RULE +
     "You must find the minimum number of minutes that must elapse until "
     "no cell has a fresh orange.\n" + _IMP +
     "Now, for the grid shown below, determine the minimum number of "
     "minutes that must elapse until no cell has a fresh orange:\n"),
)


def fields(entry):
    q = entry["question"]
    if not q.startswith(_PREFIX[0]):
        raise ValueError("rotten_oranges preamble mismatch")
    grid = q[len(_PREFIX[0]):]
    md = entry["metadata"]
    expect = "\n".join(" ".join(str(c) for c in row)
                       for row in md["matrix"]) + "\n"
    if grid != expect:
        raise ValueError("metadata matrix not verbatim in question")
    return {"grid": grid}


def render(f, v):
    return _PREFIX[v] + f["grid"]


def parse(text):
    for prefix in _PREFIX:
        if not text.startswith(prefix):
            continue
        grid = text[len(prefix):]
        if not grid or not grid.endswith("\n"):
            raise ValueError("rotten_oranges grid block malformed")
        return {"grid": grid}
    raise ValueError("no rotten_oranges pattern")
