"""Perturbation module: n_queens.

Original template: a 4-paragraph preamble (task description + attack rule +
placement mechanic + output-format directive) followed by "Given the below
board of size {n} x {n} your job is to place {k} queen(s) on the board such
that no two queens attack each other.\n{board}" — metadata carries `puzzle`
(list of 'Q'/'_' rows matching the board byte-for-byte) and `num_removed`
(== k); `solutions`/`valid_answers` are never read or leaked. The board block
is byte-verbatim in every variant, as are the attack-rule, placement-mechanic
and output-format sentences; variants rephrase only the opening task sentence
and the board lead-in. Same surface at every difficulty level (only k moves).
"""
from __future__ import annotations

import re

K = 3

# Verbatim in every variant: attack rule + placement mechanic + output format.
_PRE_REST = (
    "No two queens attack each other if they are not in the same row, "
    "column, or diagonal.\n\n"
    "You can place a queen by replacing an underscore (_) with a Q.\n\n"
    "Your output should be also a board in the same format as the input, "
    "with queens placed on the board by replacing underscores with the "
    "letter Q.\n\n"
)

_P1 = (
    "Your job is to complete an n x n chess board with n Queens in total, "
    "such that no two attack each other.\n\n",
    "Complete the n x n chess board below with n Queens in total, so that "
    "no two of them attack each other.\n\n",
    "You are asked to fill in an n x n chess board so that it holds n "
    "Queens in total and no two attack each other.\n\n",
)

_LEAD_RE = (
    re.compile(r"Given the below board of size (\d+) x (\d+) your job is to "
               r"place (\d+) queen\(s\) on the board such that no two queens "
               r"attack each other\.\n(.+\n)\Z", re.S),
    re.compile(r"The board below has size (\d+) x (\d+); place (\d+) "
               r"queen\(s\) on it such that no two queens attack each "
               r"other\.\n(.+\n)\Z", re.S),
    re.compile(r"Board size: (\d+) x (\d+)\. Place (\d+) queen\(s\) on the "
               r"board below such that no two queens attack each other\.\n"
               r"(.+\n)\Z", re.S),
)


def _lead(f, v):
    n, k = f["n"], f["k"]
    if v == 0:
        return (f"Given the below board of size {n} x {n} your job is to "
                f"place {k} queen(s) on the board such that no two queens "
                f"attack each other.\n")
    if v == 1:
        return (f"The board below has size {n} x {n}; place {k} queen(s) on "
                f"it such that no two queens attack each other.\n")
    return (f"Board size: {n} x {n}. Place {k} queen(s) on the board below "
            f"such that no two queens attack each other.\n")


def fields(entry):
    q = entry["question"]
    prefix = _P1[0] + _PRE_REST
    if not q.startswith(prefix):
        raise ValueError("n_queens preamble mismatch")
    m = _LEAD_RE[0].match(q[len(prefix):])
    if not m:
        raise ValueError("n_queens lead-in/board mismatch")
    n1, n2, k, board = m.groups()
    if n1 != n2:
        raise ValueError("n_queens board size not square")
    f = {"n": int(n1), "k": int(k), "board": board}
    md = entry["metadata"]
    expect = "\n".join(" ".join(row) for row in md["puzzle"]) + "\n"
    if board != expect:
        raise ValueError("metadata puzzle not verbatim in question")
    if f["k"] != md["num_removed"] or f["n"] != len(md["puzzle"]):
        raise ValueError("n_queens metadata counts mismatch")
    return f


def render(f, v):
    return _P1[v] + _PRE_REST + _lead(f, v) + f["board"]


def parse(text):
    for v in range(K):
        prefix = _P1[v] + _PRE_REST
        if not text.startswith(prefix):
            continue
        m = _LEAD_RE[v].match(text[len(prefix):])
        if not m:
            raise ValueError("n_queens lead-in pattern mismatch")
        n1, n2, k, board = m.groups()
        if n1 != n2:
            raise ValueError("n_queens board size not square")
        return {"n": int(n1), "k": int(k), "board": board}
    raise ValueError("no n_queens pattern")
