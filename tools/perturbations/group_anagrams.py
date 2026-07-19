"""Perturbation module: group_anagrams.

Original template: fixed anagram-definition preamble, the any-order and
output-format directive sentences, then "Group the following list of words
into anagrams:" + a JSON list of words. Metadata carries `words` (order
preserved; `solution` is never touched). The any-order and output-format
directive sentences are preserved verbatim in every variant; only the
surrounding phrasing and the word-list layout change.
"""
from __future__ import annotations

import json
import re

K = 3

_DEF = ("An anagram is a word formed by rearranging the letters of a "
        "different word, using all the original letters exactly once.")
_ANY_ORDER = "You can return the answer in any order."
_FMT = ('The output is a list of lists of strings, where each outer list '
        'contains a group of anagrams, e.g. [["eat", "tea"], ["tan", "nat"]].')


def fields(entry):
    words = tuple(entry["metadata"]["words"])
    q = entry["question"]
    if not words or not all(w in q for w in words):
        raise ValueError("metadata words not in question")
    return {"words": words}


def render(f, v):
    words = f["words"]
    if v == 0:
        return (f"{_DEF}\n\nYour job is to group the anagrams together. "
                f"{_ANY_ORDER}\n\n{_FMT}\n\n"
                f"Group the following list of words into anagrams:\n"
                f"{json.dumps(list(words))}\n")
    if v == 1:
        bullets = "\n".join(f"- {w}" for w in words)
        return (f"{_DEF}\n\nGroup the anagrams in the word list below "
                f"together. {_ANY_ORDER}\n\n{_FMT}\n\n"
                f"Word list:\n{bullets}\n")
    return (f"{_DEF}\n\nPlease group the following words into sets of "
            f"anagrams. {_ANY_ORDER}\n\n{_FMT}\n\n"
            f"Words: {', '.join(words)}\n")


def parse(text):
    m = re.search(
        r"Group the following list of words into anagrams:\n(\[.*\])\n", text)
    if m:
        return {"words": tuple(json.loads(m.group(1)))}
    m = re.search(r"Word list:\n((?:- [a-z]+\n)+)", text)
    if m:
        return {"words": tuple(l[2:] for l in m.group(1).strip().splitlines())}
    m = re.search(r"Words: ([a-z, ]+)\n", text)
    if m:
        return {"words": tuple(m.group(1).split(", "))}
    raise ValueError("no group_anagrams pattern")
