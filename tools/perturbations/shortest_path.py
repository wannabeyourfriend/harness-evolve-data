"""Perturbation module: shortest_path.

Original template: task sentence + cell-type legend + "Therefore, you need
to find ..." + movement rule + the "infeasible" directive + the
output-format directive + "Now, find the length of the shortest path from
* to # in the following grid:\n" + the * / # / O / X grid — metadata
carries `matrix` (matches the grid byte-for-byte) and `solution` (never
read or leaked). The grid block, legend, movement rule and both directive
sentences are byte-verbatim in every variant; variants rephrase only the
opening task sentence and the grid lead-in. Same surface at every
difficulty level (only the grid grows).
"""
from __future__ import annotations

K = 3

# Verbatim in every variant: legend + path/movement rules + directives.
_CORE = (
    "The grid is represented as a matrix with the following types of "
    "cells:\n"
    "- *: your starting point\n"
    "- #: your destination point\n"
    "- O: an open cell\n"
    "- X: a blocked cell\n\n"
    "Therefore, you need to find the shortest path from * to #, moving "
    "only through open cells.\n\n"
    "You may only move in four directions: up, down, left, and right.\n\n"
    'If there is no path from * to #, simply write "infeasible" (without '
    "quotes).\n\n"
    "Your output should be a sequence of directions that leads from * to "
    "#, e.g. right right down down up left\n\n"
)

_S1 = (
    "Your task is to find the shortest path from the start to the "
    "destination point in a grid.\n\n",
    "In this task, you must find the shortest path from the start to the "
    "destination point in a grid.\n\n",
    "Your goal is to find the shortest path from the start point to the "
    "destination point in a grid.\n\n",
)

_LEAD = (
    "Now, find the length of the shortest path from * to # in the "
    "following grid:\n",
    "Now, for the following grid, find the length of the shortest path "
    "from * to #:\n",
    "Find the length of the shortest path from * to # in the grid "
    "below:\n",
)


def fields(entry):
    q = entry["question"]
    prefix = _S1[0] + _CORE + _LEAD[0]
    if not q.startswith(prefix):
        raise ValueError("shortest_path preamble mismatch")
    grid = q[len(prefix):]
    md = entry["metadata"]
    expect = "\n".join(" ".join(row) for row in md["matrix"]) + "\n"
    if grid != expect:
        raise ValueError("metadata matrix not verbatim in question")
    return {"grid": grid}


def render(f, v):
    return _S1[v] + _CORE + _LEAD[v] + f["grid"]


def parse(text):
    for v in range(K):
        prefix = _S1[v] + _CORE + _LEAD[v]
        if not text.startswith(prefix):
            continue
        grid = text[len(prefix):]
        if not grid or not grid.endswith("\n"):
            raise ValueError("shortest_path grid block malformed")
        return {"grid": grid}
    raise ValueError("no shortest_path pattern")
