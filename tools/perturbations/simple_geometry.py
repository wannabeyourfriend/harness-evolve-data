"""Perturbation module: simple_geometry.

The source uses THREE native templates (all present at every level; verified
600 rows), each ending with the run-together directive
"Return only the angle as your answer.Do not give the units in your answer."
(no space after the preceding sentence — preserved verbatim, incl. in every
variant):
  0. "A convex polygon has {n} sides. The measures of the first {n-1}
     interior angles are: {A}. Find the measure of the last interior angle."
  1. "Given a convex polygon with {n} sides, its first {n-1} interior angles
     are: {A}. What is the measure of the remaining interior angle
     (in degrees)?"
  2. "Consider a convex {n}-gon whose first {n-1} interior angles are: {A}.
     Determine the measure of the remaining angle."

`tmpl` records the native template so v0 reproduces it exactly and variants
stay template-identifying (each keeps its distinctive opener). The angle list
is carried as a verbatim string (always ", ".join(f"{a}°") of metadata
known_angles — checked); the missing angle is never leaked. Variants: v1
spells both counts as number words (n <= 15, so single tokens); v2 rephrases
the asking sentence per template with digits.
"""
from __future__ import annotations

import re

from runs._drivers.perturbations._common import int_to_words, words_to_ints

K = 3

_DIRECTIVE = ("Return only the angle as your answer."
              "Do not give the units in your answer.")

# _BODIES[tmpl][v]; {n}/{m} = side/known-angle counts, {A} = angle list.
_BODIES = [
    [
        ("A convex polygon has {n} sides. The measures of the first {m} "
         "interior angles are: {A}. Find the measure of the last interior "
         "angle."),
        ("A convex polygon has {n} sides. The first {m} interior angles "
         "measure: {A}. What is the measure of the last interior angle?"),
    ],
    [
        ("Given a convex polygon with {n} sides, its first {m} interior "
         "angles are: {A}. What is the measure of the remaining interior "
         "angle (in degrees)?"),
        ("Given a convex polygon with {n} sides, if its first {m} interior "
         "angles are: {A}, what is the measure of the remaining interior "
         "angle (in degrees)?"),
    ],
    [
        ("Consider a convex {n}-gon whose first {m} interior angles are: "
         "{A}. Determine the measure of the remaining angle."),
        ("Consider a convex {n}-gon; its first {m} interior angles are: "
         "{A}. What is the measure of the remaining angle?"),
    ],
]
_DIGITS = r"(\d+)"
_WORDS = r"([a-z]+(?:-[a-z]+)?)"


def _body_re(tmpl_text, numpat):
    return re.compile(
        "^"
        + re.escape(tmpl_text)
        .replace(re.escape("{n}"), numpat)
        .replace(re.escape("{m}"), numpat)
        .replace(re.escape("{A}"), "(.+?)")
        + "$"
    )


# (regex, tmpl, words?) in the order parse tries them: v0 digits, v1 words
# (same body text as v0), v2 digits.
_PATTERNS = []
for _t, (_b0, _b2) in enumerate(_BODIES):
    _PATTERNS.append((_body_re(_b0, _DIGITS), _t, False))
    _PATTERNS.append((_body_re(_b0, _WORDS), _t, True))
    _PATTERNS.append((_body_re(_b2, _DIGITS), _t, False))


def fields(entry):
    q = entry["question"]
    f = parse(q)
    md = entry["metadata"]
    if f["n"] != md["n_sides"]:
        raise ValueError("metadata n_sides not in question")
    if f["angles"] != ", ".join(f"{a}°" for a in md["known_angles"]):
        raise ValueError("metadata known_angles not in question")
    if render(f, 0) != q:
        raise ValueError("geometry v0 does not reproduce the original")
    return f


def render(f, v):
    n, m = f["n"], f["n"] - 1
    if v == 1:
        body = _BODIES[f["tmpl"]][0].format(
            n=int_to_words(n), m=int_to_words(m), A=f["angles"])
    else:
        body = _BODIES[f["tmpl"]][v and 1].format(n=n, m=m, A=f["angles"])
    return body + _DIRECTIVE


def parse(text):
    if not text.endswith(_DIRECTIVE):
        raise ValueError("geometry answer directive missing")
    body = text[: len(text) - len(_DIRECTIVE)]
    for pat, tmpl, as_words in _PATTERNS:
        m = pat.match(body)
        if not m:
            continue
        if as_words:
            n_l, m_l = words_to_ints(m.group(1)), words_to_ints(m.group(2))
            if len(n_l) != 1 or len(m_l) != 1:
                raise ValueError("bad number words in geometry counts")
            n, k = n_l[0], m_l[0]
        else:
            n, k = int(m.group(1)), int(m.group(2))
        if k != n - 1:
            raise ValueError("geometry angle count is not sides - 1")
        return {"tmpl": tmpl, "n": n, "angles": m.group(3)}
    raise ValueError("no geometry template pattern")
