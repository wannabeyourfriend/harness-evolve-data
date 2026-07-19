"""Perturbation module: maze.

Original template: "Navigate from '<s>' (start) to '<g>' (goal):\n\n```
\n<grid>\n```\nLegend: '<w>' = Wall, '<p>' = Passage\n\nWhat is the
minimum number of steps to reach the goal?\nGive only the number of
steps as your final answer, no other text or formatting." — the four
marker characters are PER-INSTANCE (drawn from all printable ASCII incl.
quotes/backticks; 250 distinct combos across L1-L3), carried in metadata
start/goal/wall/path and embedded in the framing. The fenced grid, the
legend line, the question sentence and the answer directive are kept
verbatim in every variant; only the lead-in sentence is rephrased (it
must keep the start/goal markers so parse can recover them). Grid
capture is anchor-safe: a grid uses only 4 distinct chars, so no grid
line can spell the "Legend: '" tail.
"""
from __future__ import annotations

import re

K = 3

_TAIL_RE = re.compile(
    r"\n```\nLegend: '(.)' = Wall, '(.)' = Passage\n\n"
    r"What is the minimum number of steps to reach the goal\?\n"
    r"Give only the number of steps as your final answer, "
    r"no other text or formatting\.$"
)
_LEAD_RES = (
    re.compile(r"^Navigate from '(.)' \(start\) to '(.)' \(goal\):\n\n```\n"),
    re.compile(r"^Find your way from '(.)' \(start\) to '(.)' \(goal\) "
               r"in the maze below:\n\n```\n"),
    re.compile(r"^In the maze that follows, travel from '(.)' \(start\) "
               r"to '(.)' \(goal\):\n\n```\n"),
)


def _lead(f, v):
    s, g = f["start"], f["goal"]
    if v == 0:
        return f"Navigate from '{s}' (start) to '{g}' (goal):"
    if v == 1:
        return (f"Find your way from '{s}' (start) to '{g}' (goal) "
                "in the maze below:")
    return (f"In the maze that follows, travel from '{s}' (start) "
            f"to '{g}' (goal):")


def _tail(f):
    return (f"\n```\nLegend: '{f['wall']}' = Wall, '{f['path']}' = Passage\n\n"
            "What is the minimum number of steps to reach the goal?\n"
            "Give only the number of steps as your final answer, "
            "no other text or formatting.")


def fields(entry):
    md = entry["metadata"]
    f = {"start": md["start"], "goal": md["goal"], "wall": md["wall"],
         "path": md["path"], "grid": "\n".join(md["grid"])}
    if entry["question"] != render(f, 0):
        raise ValueError("maze question != canonical reconstruction")
    return f


def render(f, v):
    return _lead(f, v) + "\n\n```\n" + f["grid"] + _tail(f)


def parse(text):
    tm = _TAIL_RE.search(text)
    if not tm:
        raise ValueError("maze legend/directive tail missing")
    for lead in _LEAD_RES:
        lm = lead.match(text)
        if lm:
            return {"start": lm.group(1), "goal": lm.group(2),
                    "wall": tm.group(1), "path": tm.group(2),
                    "grid": text[lm.end():tm.start()]}
    raise ValueError("no maze lead pattern")
