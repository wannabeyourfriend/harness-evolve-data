"""Perturbation module: color_cube_rotation.

Original surface (verified 600 rows, L1/L2/L3 dev+heldout):
"A cube has:\n- a {color} top side\n... (fixed side order top, right, front,
left, back, bottom; article always 'a', even 'a orange')\n\n<rotation
paragraphs>\n\nWhat is now the color of the {target} side of the cube?\n
Provide only the color as your final answer."

The rotation body uses FIVE native sentence templates chosen per step ("The
cube is rotated so that the side which was before at the X is now at the
top." / "After that the cube is turned to make the X face the top." / "Then
the cube is rotated to bring the X side to the top." / "Next, the X side is
rotated to become the top face." / "Now the cube is rotated to place its X
side at the top."), so the whole rotation block is carried as a verbatim
field (byte-identical in every variant), sanity-checked against metadata
`rotations`. Colors are single words (16 seen). Variants restyle only the
color-list block and the asking sentence; "Provide only the color as your
final answer." is verbatim everywhere.
"""
from __future__ import annotations

import re

K = 3

_SIDES = ("top", "right", "front", "left", "back", "bottom")
_SIDE_ALT = "|".join(_SIDES)
_DIRECTIVE = "Provide only the color as your final answer."

_INTROS = [
    "A cube has:",
    "A cube has the following sides:",
    "The sides of a cube are colored as follows:",
]
_LINE_FMTS = [
    "- a {color} {side} side",
    "- {side} side: {color}",
    "- the {side} side is {color}",
]
_LINE_RES = [
    re.compile(rf"^- a (\S+) ({_SIDE_ALT}) side$"),
    re.compile(rf"^- ({_SIDE_ALT}) side: (\S+)$"),
    re.compile(rf"^- the ({_SIDE_ALT}) side is (\S+)$"),
]
_TAILS = [
    "What is now the color of the {t} side of the cube?\n" + _DIRECTIVE,
    "What color is the {t} side of the cube now?\n" + _DIRECTIVE,
    "Now, what is the color of the {t} side of the cube?\n" + _DIRECTIVE,
]
_TAIL_RES = [
    re.compile(
        "^"
        + re.escape(t).replace(re.escape("{t}"), f"({_SIDE_ALT})")
        + "$"
    )
    for t in _TAILS
]


def fields(entry):
    q = entry["question"]
    f = parse(q)
    md = entry["metadata"]
    if f["colors"] != tuple(md["initial_state"][s] for s in _SIDES):
        raise ValueError("metadata initial_state not in question")
    if f["target"] != md["target_side"]:
        raise ValueError("metadata target_side not in question")
    paras = f["body"].split("\n\n")
    rots = md["rotations"]
    if len(paras) != len(rots) or not all(
            s in p for s, p in zip(rots, paras)):
        raise ValueError("metadata rotations not in rotation body")
    if render(f, 0) != q:
        raise ValueError("cube v0 does not reproduce the original question")
    return f


def render(f, v):
    lines = [_INTROS[v]] + [
        _LINE_FMTS[v].format(color=c, side=s)
        for c, s in zip(f["colors"], _SIDES)
    ]
    tail = _TAILS[v].format(t=f["target"])
    return "\n".join(lines) + f"\n\n{f['body']}\n\n{tail}"


def parse(text):
    paras = text.split("\n\n")
    if len(paras) < 3:
        raise ValueError("cube paragraphs missing")
    head, body, tail = paras[0], "\n\n".join(paras[1:-1]), paras[-1]
    lines = head.split("\n")
    if len(lines) != 7 or lines[0] not in _INTROS:
        raise ValueError("no cube intro pattern")
    v = _INTROS.index(lines[0])
    colors = []
    for line, side in zip(lines[1:], _SIDES):
        m = _LINE_RES[v].match(line)
        if not m:
            raise ValueError(f"cube color line malformed: {line!r}")
        color = m.group(1) if v == 0 else m.group(2)
        got_side = m.group(2) if v == 0 else m.group(1)
        if got_side != side:
            raise ValueError("cube side order unexpected")
        colors.append(color)
    tm = next((p.match(tail) for p in _TAIL_RES if p.match(tail)), None)
    if tm is None:
        raise ValueError("no cube question tail pattern")
    return {"colors": tuple(colors), "body": body, "target": tm.group(1)}
