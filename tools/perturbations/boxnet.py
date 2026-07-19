"""Perturbation module: boxnet.

Original template: leading newline + one opening sentence on its own line +
a long constant instruction block (rules 1-7 + JSON action-plan format
example, ~2 KB) + "The current left boxes and agents are: " + the agent/box
state listing, ending "\n\n" — metadata carries row_num/column_num (the
state lists exactly row_num*column_num agents) and `initial_state` (never
read or leaked). The instruction block and the JSON-ish state description
are byte-verbatim in every variant (captured as fields via stable anchors);
variants rephrase only the opening sentence and the state lead-in. Same
surface at every difficulty level (only the field grows).
"""
from __future__ import annotations

K = 3

_S1 = (
    "You are a central planner tasked with directing agents in a grid-like "
    "field to move colored boxes to their corresponding color-coded "
    "targets.\n",
    "You serve as a central planner directing agents in a grid-like field, "
    "tasked with moving colored boxes to their corresponding color-coded "
    "targets.\n",
    "As a central planner, your task is to direct agents in a grid-like "
    "field so that colored boxes are moved to their corresponding "
    "color-coded targets.\n",
)

_MARK = (
    "The current left boxes and agents are: ",
    "The boxes and agents currently left are: ",
    "At present, the left boxes and agents are: ",
)


def _split(text, s1_opts, mark_opts):
    if not text.startswith("\n"):
        raise ValueError("boxnet leading newline missing")
    s1_hits = [s for s in s1_opts if text.startswith("\n" + s)]
    if len(s1_hits) != 1:
        raise ValueError("boxnet opening sentence mismatch")
    s1 = s1_hits[0]
    mark_hits = [m for m in mark_opts if m in text]
    if len(mark_hits) != 1:
        raise ValueError("boxnet state lead-in mismatch")
    mark = mark_hits[0]
    idx = text.find(mark)
    mid = text[len("\n" + s1):idx]
    state = text[idx + len(mark):]
    if mark in state:
        raise ValueError("boxnet state lead-in repeated")
    if not mid.startswith("Each agent occupies a 1x1 square"):
        raise ValueError("boxnet instruction block anchor missing")
    if not state.startswith("Agent[") or not state.endswith("\n\n"):
        raise ValueError("boxnet state block malformed")
    return {"mid": mid, "state": state}


def fields(entry):
    f = _split(entry["question"], _S1[:1], _MARK[:1])
    md = entry["metadata"]
    n_agents = f["state"].count("I am in square[")
    if n_agents != md["row_num"] * md["column_num"]:
        raise ValueError("boxnet agent count != row_num*column_num")
    return f


def render(f, v):
    return "\n" + _S1[v] + f["mid"] + _MARK[v] + f["state"]


def parse(text):
    return _split(text, _S1, _MARK)
