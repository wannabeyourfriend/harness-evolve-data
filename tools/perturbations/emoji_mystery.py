"""Perturbation module: emoji_mystery.

Layout (uniform across L1/L2/L3 dev+heldout, verified 2026-07-19):
    "The following emoji is encoded with a sentence.\n\n"
    "Decode the following sentence from the emoji: <PAYLOAD>"
    "\n\nHere is a hint:\n<FENCE>"
    "\n\n\nReturn the secret sentence as your final answer.\n"

PAYLOAD = base emoji + Unicode variation-selector codepoints (the encoded
sentence) and FENCE = the ```python decode-snippet block — both byte-for-byte
verbatim. All slicing is raw codepoint string ops; no normalization or
re-encoding anywhere. The final answer-format directive sentence is kept
verbatim in every variant; variants rephrase only the intro sentence, the
payload lead-in, and the hint label. metadata sentence content is never read.
"""
from __future__ import annotations

K = 3

_TAIL = "\n\n\nReturn the secret sentence as your final answer.\n"

# (intro, lead, hint-label) per variant. Payload contains no newlines, so
# the "\n\n"-prefixed hint labels can never collide with it.
_FRAMES = (
    ("The following emoji is encoded with a sentence.\n\n",
     "Decode the following sentence from the emoji: ",
     "\n\nHere is a hint:\n"),
    ("The emoji below has a hidden sentence encoded in it.\n\n",
     "Recover the sentence encoded in this emoji: ",
     "\n\nHere is a hint:\n"),
    ("Hidden within the following emoji is a sentence.\n\n",
     "Decode the sentence concealed in the emoji: ",
     "\n\nAs a hint, here is a Python snippet:\n"),
)


def _split(text):
    for intro, lead, hint in _FRAMES:
        prefix = intro + lead
        if not text.startswith(prefix):
            continue
        if not text.endswith(_TAIL):
            raise ValueError("emoji_mystery tail directive missing")
        hidx = text.find(hint, len(prefix))
        if hidx < 0:
            raise ValueError("emoji_mystery hint label missing")
        payload = text[len(prefix):hidx]
        if "\n" in payload or not payload:
            raise ValueError("unexpected emoji payload")
        fence = text[hidx + len(hint): -len(_TAIL)]
        if not (fence.startswith("```python\n") and fence.endswith("```")):
            raise ValueError("unexpected emoji hint fence")
        return {"payload": payload, "fence": fence}
    raise ValueError("no emoji_mystery pattern")


def fields(entry):
    q = entry["question"]
    f = _split(q)
    emoji = entry.get("metadata", {}).get("emoji")
    if emoji and not f["payload"].startswith(emoji):
        raise ValueError("metadata emoji not at payload start")
    if render(f, 0) != q:
        raise ValueError("emoji_mystery v0 reconstruction mismatch")
    return f


def render(f, v):
    intro, lead, hint = _FRAMES[v]
    return f"{intro}{lead}{f['payload']}{hint}{f['fence']}{_TAIL}"


def parse(text):
    return _split(text)
