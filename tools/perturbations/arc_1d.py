"""Perturbation module: arc_1d.

Original template: "Find the common rule ..." header + the Example 1..3
Input/Output blocks + "\nBelow is a test input grid. Predict the
corresponding output grid by applying the rule you found. <describe-your-
reasoning + final-answer directives>\n\nInput:\n" + the test input row (no
trailing newline) — metadata carries train_examples/test_example, which the
question shows verbatim (sanity-checked byte-for-byte; nothing else is
read or leaked). ALL example blocks and the test row are byte-verbatim in
every variant (they ARE the task), as are the "Describe how you derived
the rule ..." / "Your final answer should be ..." directive sentences and
the "Input:" label; variants rephrase only the header sentence and the
"Below is a test input grid. Predict ..." lead-in. Same surface at every
difficulty level (only the rows grow); always 3 examples.
"""
from __future__ import annotations

K = 3

_HEAD = (
    "Find the common rule that maps an input grid to an output grid, given "
    "the examples below.\n\n",
    "Study the examples below and find the common rule that maps an input "
    "grid to an output grid.\n\n",
    "Given the examples below, work out the common rule that maps an input "
    "grid to an output grid.\n\n",
)

_DIRECTIVES = (
    "Describe how you derived the rule and your overall reasoning process "
    "in detail before you submit your answer. Your final answer should be "
    "just the test output grid itself.\n\nInput:\n")

_MID = (
    "\nBelow is a test input grid. Predict the corresponding output grid by "
    "applying the rule you found. " + _DIRECTIVES,
    "\nNow apply the rule you found to the test input grid below and "
    "predict the corresponding output grid. " + _DIRECTIVES,
    "\nA test input grid follows; apply the rule you found to it and "
    "predict the corresponding output grid. " + _DIRECTIVES,
)


def _split(text, head_opts, mid_opts):
    head_hits = [h for h in head_opts if text.startswith(h)]
    if len(head_hits) != 1:
        raise ValueError("arc_1d header mismatch")
    head = head_hits[0]
    mid_hits = [m for m in mid_opts if m in text]
    if len(mid_hits) != 1:
        raise ValueError("arc_1d test lead-in mismatch")
    mid = mid_hits[0]
    idx = text.find(mid)
    examples = text[len(head):idx]
    test = text[idx + len(mid):]
    if not examples.startswith("Example 1:\nInput:  ") \
            or not examples.endswith("\n"):
        raise ValueError("arc_1d examples block malformed")
    if not test or "\n" in test:
        raise ValueError("arc_1d test row malformed")
    return {"examples": examples, "test": test}


def fields(entry):
    f = _split(entry["question"], _HEAD[:1], _MID[:1])
    md = entry["metadata"]
    expect = "\n\n".join(
        f"Example {j + 1}:\nInput:  "
        + " ".join(str(x) for x in ex["input"])
        + "\nOutput: " + " ".join(str(x) for x in ex["output"])
        for j, ex in enumerate(md["train_examples"])) + "\n"
    if f["examples"] != expect:
        raise ValueError("metadata train_examples not verbatim in question")
    if f["test"] != " ".join(str(x) for x in md["test_example"]["input"]):
        raise ValueError("metadata test input not verbatim in question")
    return f


def render(f, v):
    return _HEAD[v] + f["examples"] + _MID[v] + f["test"]


def parse(text):
    return _split(text, _HEAD, _MID)
