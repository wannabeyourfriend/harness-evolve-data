"""Perturbation module: knight_swap.

Original template: "Knight Swap Challenge:\n\n```\n<board diagram>```" +
Legend + Objective sentence + Rules (rule 3 is parametrized by the starting
side: "w moves first" or "B moves first" — 25/300 rows start with B, matching
metadata `start_turn`) + Question + Answer Format — metadata also carries
`pieces` (sanity-checked against the board cells), plus `is_possible` /
`solution` / `board_states`, which are never read or leaked. The fenced
board diagram, Legend, Rules, Question and Answer Format blocks are
byte-verbatim in every variant; variants rephrase only the challenge header
and the Objective sentence. Same surface at every difficulty level (only
the board population differs).
"""
from __future__ import annotations

import re

K = 3

_HDR = (
    "Knight Swap Challenge:\n\n```\n",
    "Here is a Knight Swap puzzle:\n\n```\n",
    "Consider the following Knight Swap challenge:\n\n```\n",
)

_OBJ = (
    "Swap the positions of all white knights with all black knights "
    "through valid moves.",
    "Through a sequence of valid moves, swap the positions of all white "
    "knights with all black knights.",
    "Your goal is to swap the positions of all white knights with all "
    "black knights using only valid moves.",
)

_LEGEND = ("```\n\nLegend:\n- 'w' = White Knight\n- 'B' = Black Knight\n"
           "- Empty squares are marked with '.'\n\nObjective:\n")


def _tail(start):
    return (
        "\n\nRules:\n"
        "1. Knights move in L-shape (2 squares + 1 square perpendicular)\n"
        "2. Knights can only move to empty squares\n"
        f"3. {start} moves first, then players alternate\n"
        "4. All knights must reach their target positions (white ↔ "
        "black)\n\n"
        "Question:\nIs it possible to swap all knights' positions? If yes, "
        "list the moves.\n\n"
        "Answer Format:\n"
        '- For impossible puzzles: "No"\n'
        '- For possible puzzles: List moves as ["color,from,to", ...]\n'
        '  Example: ["w,A1,B3"] means white knight moves A1→B3\n')


def _split(text, hdr_opts, obj_opts):
    hdr_hits = [h for h in hdr_opts if text.startswith(h)]
    if len(hdr_hits) != 1:
        raise ValueError("knight_swap header mismatch")
    rest = text[len(hdr_hits[0]):]
    idx = rest.find(_LEGEND)
    if idx < 0:
        raise ValueError("knight_swap legend anchor missing")
    board = rest[:idx]
    if "```" in board or not board.endswith("\n"):
        raise ValueError("knight_swap board block malformed")
    after = rest[idx + len(_LEGEND):]
    for obj in obj_opts:
        for start in ("w", "B"):
            if after == obj + _tail(start):
                return {"board": board, "start": start}
    raise ValueError("knight_swap objective/rules block mismatch")


def fields(entry):
    f = _split(entry["question"], _HDR[:1], _OBJ[:1])
    md = entry["metadata"]
    if f["start"] != md["start_turn"]:
        raise ValueError("knight_swap start_turn mismatch")
    nw = nb = 0
    for line in f["board"].split("\n"):
        m = re.match(r"^(\d+) \|(.*)$", line)
        if not m:
            continue
        for cell in m.group(2).split("|"):
            cell = cell.strip()
            if cell == "w":
                nw += 1
            elif cell == "B":
                nb += 1
    pieces = md["pieces"]
    if nw != sum(1 for p in pieces.values() if p == "w") \
            or nb != sum(1 for p in pieces.values() if p == "B"):
        raise ValueError("metadata pieces not matching board diagram")
    return f


def render(f, v):
    return _HDR[v] + f["board"] + _LEGEND + _OBJ[v] + _tail(f["start"])


def parse(text):
    return _split(text, _HDR, _OBJ)
