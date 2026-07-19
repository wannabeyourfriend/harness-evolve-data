"""Perturbation module: letter_jumble.

Original template: a fixed instruction preamble (incl. the source's
"unsramble" typo, the order/style-preservation notes, and the output-format
sentence — all preserved verbatim as `head`) followed by "Now, unscramble
these words: <scrambled sentence>\n" — metadata carries `scrambled_words`
(joined with single spaces in the question) and `original_words`, which is
never read or leaked. The scrambled sentence appears byte-identical in every
variant; variants rephrase only the final lead-in.
"""
from __future__ import annotations

K = 3
_MARK0 = "Now, unscramble these words: "
_MARK1 = "Please unscramble the words in this sentence: "
_MARK2 = "Scrambled sentence to unscramble:\n"


def fields(entry):
    sent = " ".join(entry["metadata"]["scrambled_words"])
    q = entry["question"]
    if sent not in q:
        raise ValueError("metadata scrambled_words not in question")
    idx = q.find(_MARK0)
    if idx < 0:
        raise ValueError("letter_jumble marker missing")
    head = q[:idx]
    if q != f"{head}{_MARK0}{sent}\n":
        raise ValueError("unexpected letter_jumble layout")
    return {"head": head, "sentence": sent}


def render(f, v):
    mark = (_MARK0, _MARK1, _MARK2)[v]
    return f"{f['head']}{mark}{f['sentence']}\n"


def parse(text):
    for mark in (_MARK0, _MARK1, _MARK2):
        idx = text.find(mark)
        if idx < 0:
            continue
        rest = text[idx + len(mark):]
        if not rest.endswith("\n"):
            raise ValueError("letter_jumble payload missing trailing newline")
        return {"head": text[:idx], "sentence": rest[:-1]}
    raise ValueError("no letter_jumble pattern")
