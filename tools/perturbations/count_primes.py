"""Perturbation module: count_primes.

Original template (uniform across all L1/L2/L3 dev+heldout rows):
"Count how many prime numbers there are between X and Y (inclusive) ?" —
metadata carries start/end (never the primes/solution fields, which are not
touched). K=3: v1 spells the bounds as number words (bounds reach ~50000 at
L3; int_to_words handles thousands), v2 rewords with a bracketed range.
The original has no answer-format directive tail, so none is added; the
inclusive-endpoints semantics is preserved in every variant.
"""
from __future__ import annotations

import re

from runs._drivers.perturbations._common import int_to_words, words_to_ints

K = 3


def fields(entry):
    md = entry["metadata"]
    f = {"start": md["start"], "end": md["end"]}
    q = entry["question"]
    if str(f["start"]) not in q or str(f["end"]) not in q:
        raise ValueError("metadata start/end not in question")
    return f


def render(f, v):
    if v == 0:
        return (f"Count how many prime numbers there are between "
                f"{f['start']} and {f['end']} (inclusive) ?")
    if v == 1:
        return (f"Count the prime numbers from {int_to_words(f['start'])} "
                f"through {int_to_words(f['end'])}, including both endpoints.")
    return (f"Inclusive range [{f['start']}, {f['end']}]: how many prime "
            f"numbers does it contain?")


def parse(text):
    m = re.search(r"between (\d+) and (\d+) \(inclusive\) \?", text)
    if m:
        return {"start": int(m.group(1)), "end": int(m.group(2))}
    m = re.search(r"from ([a-z\- ]+) through ([a-z\- ]+), including both endpoints\.",
                  text)
    if m:
        return {"start": words_to_ints(m.group(1))[0],
                "end": words_to_ints(m.group(2))[0]}
    m = re.search(r"Inclusive range \[(\d+), (\d+)\]: how many prime numbers "
                  r"does it contain\?", text)
    if m:
        return {"start": int(m.group(1)), "end": int(m.group(2))}
    raise ValueError("no count_primes pattern")
