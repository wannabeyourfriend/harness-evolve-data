"""Perturbation module: power_function.

Ported from the metadata-route spec in runs/_drivers/build_fmt_tier1.py.
The tail carries BOTH answer-format directives — "3 significant figures"
AND "scientific notation using 'e' notation" — and every variant embeds it
verbatim (the audited _PW_TAIL both-directives lesson: never drop either
line). Exponents on the ladder go negative (to -12 at L3); the patterns
accept signed exponents and float bases. Deviations from tier1: renders end
with the original's trailing newline so render(f, 0) is byte-identical to
the ladder originals, and the sanity check covers base^exponent plus both
directive phrases.
"""
from __future__ import annotations

import re

K = 3

_TAIL = ("Return your final answer correct to 3 significant figures.\n"
         "Provide your answer in scientific notation using 'e' notation "
         "(e.g., 1.23e+4).")


def fields(entry):
    md = entry["metadata"]
    f = {"b": md["base"], "x": md["exponent"]}
    q = entry["question"]
    if f"{f['b']}^{f['x']}" not in q:
        raise ValueError("base^exponent not in question")
    if "3 significant figures" not in q or "scientific notation" not in q:
        raise ValueError("expected answer-format directives missing from original")
    return f


def render(f, v):
    if v == 0:
        return (f"Your task is to compute an exponentiation of a number.\n\n"
                f"Compute {f['b']}^{f['x']}. {_TAIL}\n")
    if v == 1:
        return f"Raise {f['b']} to the power {f['x']}. {_TAIL}\n"
    return f"Evaluate pow({f['b']}, {f['x']}). {_TAIL}\n"


def parse(text):
    for pat in (r"Compute (-?[\d.]+)\^(-?\d+)\.",
                r"Raise (-?[\d.]+) to the power (-?\d+)\.",
                r"Evaluate pow\((-?[\d.]+), (-?\d+)\)\."):
        m = re.search(pat, text)
        if m:
            return {"b": float(m.group(1)), "x": int(m.group(2))}
    raise ValueError("no power pattern")
