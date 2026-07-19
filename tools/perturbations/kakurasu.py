"""Perturbation module: kakurasu.

Multi-template task: reasoning_gym samples one of TEN full prompt
templates per instance — a one-line intro (10 phrasings, embedding
"<R> x <C>" and the row/col sum lists, row sums always first) followed
by a numbered rules block whose wording ALSO varies per template, then
"2. Input:\n<all-zero grid>". Verified across L1-L3 dev+heldout: the
rules-block wording maps 1:1 onto the intro template, so the verbatim
tail (everything from "\n1. Rules:\n" on — rules + input grid, never
touched) determines which intro to rebuild for v0. Variants v1/v2
rephrase only the intro (keeping dims as "<R> x <C>" and both sum lists,
row-first, so one generic parser recovers the fields from any surface);
the rules block and input grid are preserved byte-verbatim. Note the
source's "Kukurasu" spelling is kept. solution/puzzle metadata is never
read.
"""
from __future__ import annotations

import re

K = 3

_ANCHOR = "\n1. Rules:\n"
_INPUT_MARK = "\n2. Input:"

# The ten source intro templates, keyed by the template id derived from
# the rules-block wording (see _template_id).
_INTROS = (
    "This is a {r} x {c} Kukurasu puzzle grid. Your task is to fill in the "
    "grid with 1s and 0s such that the weighted sums match the given "
    "constraints. The row sums are {rs} and the column sums are {cs}.",
    "This {r} x {c} grid represents a Kukurasu puzzle. Your task is to "
    "place 1s in the grid so that the weighted sums match the constraints. "
    "Row sums: {rs}. Column sums: {cs}.",
    "Below is a {r} x {c} Kukurasu puzzle grid. Your objective is to place "
    "1s in the grid such that the weighted sums of rows and columns match "
    "the given constraints. Row sums: {rs}. Column sums: {cs}.",
    "You have a {r} x {c} Kukurasu puzzle grid. Your goal is to place 1s "
    "in the grid so that the weighted sums match the given constraints: "
    "row sums {rs} and column sums {cs}.",
    "You are given a {r} x {c} grid representing a Kukurasu puzzle. In "
    "this puzzle, you need to place 1s in the grid so that the weighted "
    "sum of each row and column matches the given constraints. The row "
    "sums are {rs} and the column sums are {cs}.",
    "Examine this {r} x {c} Kukurasu puzzle grid. Your objective is to "
    "place 1s in the grid such that the weighted sums match the given "
    "constraints: row sums {rs} and column sums {cs}.",
    "I'm presenting you with a {r} x {c} Kukurasu puzzle. Your task is to "
    "place 1s in the grid so that the weighted sums match the given "
    "constraints: row sums {rs} and column sums {cs}.",
    "You're presented with a {r} x {c} Kukurasu puzzle grid. The goal is "
    "to place 1s in the grid so that the weighted sums of rows and columns "
    "match the given constraints: row sums {rs} and column sums {cs}.",
    "Here's a {r} x {c} Kukurasu logic puzzle. You need to place 1s in "
    "the grid so that the weighted sums match the constraints. Row sums: "
    "{rs}. Column sums: {cs}.",
    "Consider this {r} x {c} Kukurasu puzzle grid. You need to place 1s "
    "in the grid such that the weighted sums match the constraints. Row "
    "sums: {rs}. Column sums: {cs}.",
)


def _template_id(tail):
    """Map the verbatim rules block onto the source intro template (1:1,
    verified across L1-L3 dev+heldout)."""
    end = tail.find(_INPUT_MARK)
    rules = tail[:end] if end >= 0 else tail
    if "(positions are 1-indexed)" in rules:
        return 0
    if "A 1 in the jth position of a row" in rules:
        return 1 if "must contain" in rules else 8
    if "equals its column number" in rules:
        return 2 if "The sum of weighted 1s" in rules else 5
    if "is its column position" in rules:
        return 4 if "corresponding row constraint" in rules else 3
    if "has a weight of j" in rules:
        return 6
    if "A 1 in column j of any row" in rules:
        return 7
    if "A 1 in column position j" in rules:
        return 9
    raise ValueError("unknown kakurasu rules block")


def fields(entry):
    md = entry["metadata"]
    q = entry["question"]
    idx = q.find(_ANCHOR)
    if idx < 0:
        raise ValueError("kakurasu rules anchor missing")
    f = {"n_rows": int(md["n_rows"]), "n_cols": int(md["n_cols"]),
         "row_sums": tuple(md["row_sums"]), "col_sums": tuple(md["col_sums"]),
         "tail": q[idx:]}
    if q != render(f, 0):
        raise ValueError("kakurasu question != template reconstruction")
    return f


def render(f, v):
    r, c = f["n_rows"], f["n_cols"]
    rs, cs = str(list(f["row_sums"])), str(list(f["col_sums"]))
    if v == 0:
        intro = _INTROS[_template_id(f["tail"])].format(r=r, c=c, rs=rs,
                                                        cs=cs)
    elif v == 1:
        intro = (f"Kukurasu puzzle on a {r} x {c} grid: fill every cell "
                 "with a 1 or a 0 so that the weighted row and column sums "
                 f"hit their targets. Target row sums: {rs}. Target column "
                 f"sums: {cs}.")
    else:
        intro = (f"Solve this Kukurasu puzzle. On the {r} x {c} grid "
                 "below, place 1s so that every weighted row and column "
                 f"sum comes out right. Required row sums: {rs}; required "
                 f"column sums: {cs}.")
    return intro + f["tail"]


def parse(text):
    idx = text.find(_ANCHOR)
    if idx < 0:
        raise ValueError("kakurasu rules anchor missing")
    intro, tail = text[:idx], text[idx:]
    m = re.search(r"(\d+) x (\d+)", intro)
    lists = re.findall(r"\[([0-9, ]+)\]", intro)
    if not m or len(lists) != 2:
        raise ValueError("kakurasu intro fields missing")
    return {"n_rows": int(m.group(1)), "n_cols": int(m.group(2)),
            "row_sums": tuple(int(x) for x in lists[0].split(",")),
            "col_sums": tuple(int(x) for x in lists[1].split(",")),
            "tail": tail}
