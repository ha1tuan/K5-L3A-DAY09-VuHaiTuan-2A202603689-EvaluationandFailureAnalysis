"""M1 evidence probe: run the swarm with exactly ONE failure-mode switch on.

    python scripts/lab9_fm_probe.py --matrix                      # FM -> claims whose trials fail
    python scripts/lab9_fm_probe.py --fm FM-04 --claim C-014 --seed 11   # one trace, trace_case format

Each probe is `fixed` (no_override) + one bug switch from lab9/variant_agent.py, except FM-03
(ticket_trust replaces no_override). Nothing in lab8/ or the registered variants is changed.
FM-08 is invisible to the Lab 8 grader, so the matrix also flags reply amount != ledger refund_vnd.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # run from src/: make lab8/lab9 importable

from lab8.console import utf8_stdio  # noqa: E402
from lab8.db import load_jsonl  # noqa: E402
from lab8.shapes import SHAPES  # noqa: E402
from lab9 import trace_case  # noqa: E402
from lab9.variant_agent import make_shape  # noqa: E402

SEEDS = [11, 22, 33, 44, 55]
PROBES = {
    "FM-01": {"no_override", "leaky_trace"},
    "FM-02": {"no_override", "ignore_denied"},
    "FM-03": {"ticket_trust"},
    "FM-04": {"no_override", "sum_parts"},
    "FM-05": {"no_override", "pre_deducted"},
    "FM-06": {"no_override", "stale_clause"},
    "FM-07": {"no_override", "sibling_refund"},
    "FM-08": {"no_override", "misreport"},
}
AMOUNT = re.compile(r"hoàn ([\d.]+)đ")


def shape_name(fm: str) -> str:
    return f"probe_{fm.replace('-', '').lower()}"


def register() -> None:
    for fm, bugs in PROBES.items():
        SHAPES.setdefault(shape_name(fm), make_shape(shape_name(fm), frozenset(bugs)))


def reply_mismatch(trial: dict) -> bool:
    replies = [e["payload"]["text"] for e in trial["events"] if e.get("kind") == "reply"]
    m = AMOUNT.search(replies[-1]) if replies else None
    return bool(m) and int(m.group(1).replace(".", "")) != int(trial["snapshot"].get("refund_vnd") or 0)


def matrix() -> None:
    claims = [c["claim_id"] for c in load_jsonl(Path("data/public_claims.jsonl"))]
    for fm in PROBES:
        hits = []
        for cid in claims:
            bad = []
            for seed in SEEDS:
                t = trace_case.investigate(shape_name(fm), cid, seed)["trial"]
                if not t["lab8_pass"]:
                    bad.append(t["lab8_reason"].split(":")[0])
                elif reply_mismatch(t):
                    bad.append("reply!=ledger")
            if bad:
                hits.append(f"{cid}({len(bad)}/5 {sorted(set(bad))[0]})")
        print(f"{fm}: {', '.join(hits) or '-'}")


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9_fm_probe")
    ap.add_argument("--matrix", action="store_true")
    ap.add_argument("--fm", choices=sorted(PROBES))
    ap.add_argument("--claim")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args(argv)
    register()
    if args.matrix:
        matrix()
        return 0
    if not (args.fm and args.claim):
        ap.error("need --matrix, or --fm and --claim")
    return trace_case.main(["--shape", shape_name(args.fm), "--claim", args.claim, "--seed", str(args.seed)])


if __name__ == "__main__":
    raise SystemExit(main())
