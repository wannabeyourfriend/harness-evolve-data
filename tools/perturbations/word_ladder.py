"""Perturbation module: word_ladder.

Original template: "Transform the word ladder 'BUNS' to 'MASA' by changing
one letter at a time.\n<tail>" — metadata carries `start_word` / `end_word`.
The answer-format tail ("Provide your answer as a comma-separated sequence of
uppercase letters without spaces.\nEach step must be a valid English word.")
is preserved verbatim in every variant, and every variant keeps the
"changing one letter at a time" directive.
"""
from __future__ import annotations

import re

K = 3
_TAIL_MARK = ("Provide your answer as a comma-separated sequence of uppercase "
              "letters without spaces.")


def _split_tail(q: str) -> str:
    idx = q.find(_TAIL_MARK)
    if idx < 0:
        raise ValueError("word_ladder tail marker missing")
    return q[idx:]


def fields(entry):
    start = entry["metadata"]["start_word"]
    end = entry["metadata"]["end_word"]
    q = entry["question"]
    if f"'{start}'" not in q or f"'{end}'" not in q:
        raise ValueError("metadata start/end words not in question")
    return {"start": start, "end": end, "tail": _split_tail(q)}


def render(f, v):
    if v == 0:
        return (f"Transform the word ladder '{f['start']}' to '{f['end']}' "
                f"by changing one letter at a time.\n{f['tail']}")
    if v == 1:
        return (f"Word ladder puzzle: turn '{f['start']}' into '{f['end']}', "
                f"changing one letter at a time.\n{f['tail']}")
    return (f"Start word: '{f['start']}'\nEnd word: '{f['end']}'\n"
            f"Build a word ladder from the start word to the end word, "
            f"changing one letter at a time.\n{f['tail']}")


def parse(text):
    tail = _split_tail(text)
    head = text[: text.find(_TAIL_MARK)]
    m = re.search(r"Transform the word ladder '([A-Z]+)' to '([A-Z]+)'", head)
    if m:
        return {"start": m.group(1), "end": m.group(2), "tail": tail}
    m = re.search(r"turn '([A-Z]+)' into '([A-Z]+)'", head)
    if m:
        return {"start": m.group(1), "end": m.group(2), "tail": tail}
    m = re.search(r"Start word: '([A-Z]+)'\nEnd word: '([A-Z]+)'", head)
    if m:
        return {"start": m.group(1), "end": m.group(2), "tail": tail}
    raise ValueError("no word_ladder pattern")
