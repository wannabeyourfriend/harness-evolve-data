"""Perturbation module: caesar_cipher.

Original template (audited dev+heldout, 100/100 canonical):
    "Decrypt this Caesar cipher text: <CT>. Provide only the decrypted text
     as your final answer."
Metadata also carries clear_text and rotation — those are the SOLUTION and
must never appear in any variant, so fields() exposes only cipher_text.
The directive "Decrypt this Caesar cipher text" and the answer-format
sentence are preserved verbatim in every variant; the cipher text appears
byte-identical — never transformed.
"""
from __future__ import annotations

K = 3
_ANSWER_FMT = "Provide only the decrypted text as your final answer."
_V0_HEAD = "Decrypt this Caesar cipher text: "
_V0_TAIL = f". {_ANSWER_FMT}"
_V1_HEAD = ("The following text was encrypted with a Caesar cipher. "
            "Decrypt this Caesar cipher text:\n\n")
_V1_TAIL = f"\n\n{_ANSWER_FMT}"
_V2_HEAD = "Ciphertext:\n"
_V2_TAIL = f"\n\nDecrypt this Caesar cipher text. {_ANSWER_FMT}"


def fields(entry):
    ct = entry["metadata"]["cipher_text"]
    q = entry["question"]
    if ct not in q:
        raise ValueError("metadata cipher_text not in question")
    if "\n" in ct:
        raise ValueError("multi-line cipher_text unsupported")
    if q != f"{_V0_HEAD}{ct}{_V0_TAIL}":
        raise ValueError("non-canonical caesar_cipher question")
    return {"cipher_text": ct}


def render(f, v):
    ct = f["cipher_text"]
    if v == 0:
        return f"{_V0_HEAD}{ct}{_V0_TAIL}"
    if v == 1:
        return f"{_V1_HEAD}{ct}{_V1_TAIL}"
    return f"{_V2_HEAD}{ct}{_V2_TAIL}"


def parse(text):
    for head, tail in ((_V1_HEAD, _V1_TAIL), (_V2_HEAD, _V2_TAIL),
                       (_V0_HEAD, _V0_TAIL)):
        if text.startswith(head) and text.endswith(tail):
            return {"cipher_text": text[len(head):-len(tail)]}
    raise ValueError("no caesar_cipher pattern")
