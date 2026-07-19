"""Perturbation module: codeio.

Two modes across L1/L2/L3 dev+heldout (135 predict-input / 165
predict-output of 300, verified 2026-07-19), one layout each:

    "\nYou are given a question that requires some input and output
     variables as follows:\n\n" <QUERY>
    "\n\nThe input and output requirements are as follows:\n\n" <IOREQ>
    "\n\nGiven the following output:\n\n" <VALUE>      (or "... input ...")
    <ASK directive sentence for the mode>
    "Tip: Here is a reference code snippet ... not copy spans of code
     directly.\n\n" <CODE>

QUERY / IOREQ / VALUE / CODE are verbatim bodies (questions run 3-14k
chars). The two mode-specific ASK sentences are answer-format directives
and the Tip sentence constrains solver behavior — all three kept verbatim
in every variant. Variants rephrase only the three framing labels (head
sentence, io-requirements label, given-value label). Parsing anchors on
the invariant ASK/Tip directives plus per-variant labels, with
uniqueness (count == 1) asserts so a body-text collision fails closed
(verify() then falls back to the original question). metadata
input_data/output_data are not read: their str() form differs from the
rendered value on ~35% of rows after JSON round-trip; the sanity check is
instead an exact v0 reconstruction of the whole question.
"""
from __future__ import annotations

K = 3

_ASK = {
    "in": (
        "\n\nCan you predict a feasible input without writing any code? "
        "Please reason and put your final answer in the form of a JSON value "
        "(object, array, number or string, or one of the following three "
        "literal names: false null true), even if the there is only one "
        "input variable, with keys strictly matching the input variables' "
        "names as specified.\n\n"
    ),
    "out": (
        "\n\nCan you predict the output without writing any code? Please "
        "think and then provide the exact output in the form of a JSON value "
        "(object, array, number or string, or one of the following three "
        "literal names: false null true) as your final answer. The keys and "
        "values of the object should strictly match the output requirement "
        "as specified.\n\n"
    ),
}
_TIP = (
    "Tip: Here is a reference code snippet for this question. You can refer "
    "to this code to guide your reasoning but not copy spans of code "
    "directly.\n\n"
)

# Per-variant framing: (head, ioreq label, given-output label,
# given-input label). No label is a substring of another variant's.
_FRAMES = (
    ("\nYou are given a question that requires some input and output "
     "variables as follows:\n\n",
     "\n\nThe input and output requirements are as follows:\n\n",
     "\n\nGiven the following output:\n\n",
     "\n\nGiven the following input:\n\n"),
    ("\nBelow is a question that involves some input and output variables:"
     "\n\n",
     "\n\nHere are the input and output requirements:\n\n",
     "\n\nThe following output was produced:\n\n",
     "\n\nThe following input was provided:\n\n"),
    ("\nConsider a question that requires some input and output variables, "
     "stated as follows:\n\n",
     "\n\nThe requirements for the input and output variables are as "
     "follows:\n\n",
     "\n\nObserve the following output:\n\n",
     "\n\nObserve the following input:\n\n"),
)


def _one(text, marker, what):
    n = text.count(marker)
    if n != 1:
        raise ValueError(f"codeio {what} marker count {n} != 1")
    return text.find(marker)


def _split(text):
    if _ASK["in"] in text:
        mode = "in"
    elif _ASK["out"] in text:
        mode = "out"
    else:
        raise ValueError("codeio ask directive missing")
    aidx = _one(text, _ASK[mode], "ask")
    rest = text[aidx + len(_ASK[mode]):]
    if not rest.startswith(_TIP):
        raise ValueError("codeio Tip directive missing after ask")
    code = rest[len(_TIP):]
    for head, ioreq, gout, gin in _FRAMES:
        if not text.startswith(head):
            continue
        given = gout if mode == "in" else gin
        ridx = _one(text, ioreq, "io-requirements")
        gidx = _one(text, given, "given-value")
        if not len(head) <= ridx < gidx < aidx:
            raise ValueError("codeio sections out of order")
        return {
            "mode": mode,
            "query": text[len(head):ridx],
            "ioreq": text[ridx + len(ioreq):gidx],
            "value": text[gidx + len(given):aidx],
            "code": code,
        }
    raise ValueError("no codeio head pattern")


def fields(entry):
    q = entry["question"]
    f = _split(q)
    if not (f["query"] and f["ioreq"] and f["value"] and f["code"]):
        raise ValueError("empty codeio section")
    if f["code"] not in q:  # literal-appearance sanity (trivially true)
        raise ValueError("code not in question")
    if render(f, 0) != q:
        raise ValueError("codeio v0 reconstruction mismatch")
    return f


def render(f, v):
    head, ioreq, gout, gin = _FRAMES[v]
    given = gout if f["mode"] == "in" else gin
    return (f"{head}{f['query']}{ioreq}{f['ioreq']}{given}{f['value']}"
            f"{_ASK[f['mode']]}{_TIP}{f['code']}")


def parse(text):
    return _split(text)
