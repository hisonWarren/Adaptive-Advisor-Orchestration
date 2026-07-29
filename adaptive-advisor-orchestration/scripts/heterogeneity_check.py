#!/usr/bin/env python3
"""
heterogeneity_check.py — mechanize the panel's deepest guard.

The skill's hardest-to-enforce discipline is pseudo-diversity detection: a model
eyeballs role cards and asserts "these look different" without actually checking.
This script forces the check. It parses role cards, compares every pair on red
lines and evaluation criteria, and refuses to pass unless the adversary's roster
review has named a shared assumption. It never claims two roles ARE heterogeneous
by meaning — token overlap is only a cheap signal — but it catches the obvious
collapses the model would otherwise wave through, and it enforces the process
gate (named shared assumption, present outsider) that the model tends to skip.

Input: a JSON file describing the roster. Schema:
{
  "roles": [
    {"name": "...", "red_line": "...", "criteria": "...", "is_outsider": false,
     "veto_reason": "why this role would veto the current draft"},
    ...
  ],
  "roster_review": {
    "shared_assumption_named": "the one assumption no role would challenge, or null",
    "regenerated": false
  }
}

Usage:
  python scripts/heterogeneity_check.py roster.json
  python scripts/heterogeneity_check.py roster.json --threshold 0.6

Exit code 0 = pass, 1 = fail (with reasons printed). Designed to be run by the
facilitator at the end of Phase 1, before construction.
"""
import argparse
import json
import re
import sys
from itertools import combinations


def tokens(text):
    return set(re.findall(r"[a-z0-9\u4e00-\u9fff]+", (text or "").lower()))


def jaccard(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def check(roster, threshold):
    failures = []
    warnings = []
    roles = roster.get("roles", [])

    # Schema guard: catch the common wrong shapes early with an actionable message,
    # instead of silently doing a weaker check (e.g. criteria given as a list, or
    # the review key mis-named). This is what makes "call the packaged script"
    # safe — a wrong schema fails loudly rather than passing a degraded check.
    schema_errors = []
    for r in roles:
        if isinstance(r.get("criteria"), list):
            schema_errors.append(
                f"role '{r.get('name','?')}': 'criteria' must be a string, got a list. "
                f"Join it, e.g. \"stability; low burden; breadth\"."
            )
        if "red_line" not in r or "criteria" not in r:
            schema_errors.append(f"role '{r.get('name','?')}': missing 'red_line' or 'criteria'.")
    if "roster_review" not in roster and "shared_assumption_checked" in roster:
        schema_errors.append(
            "found 'shared_assumption_checked' but the schema is "
            "roster_review.shared_assumption_named. Wrap it: "
            "\"roster_review\": {\"shared_assumption_named\": \"...\"}."
        )
    if schema_errors:
        print("SCHEMA ERROR — fix the input file and rerun (do not fall back to an inline check):")
        for e in schema_errors:
            print(f"  - {e}")
        print("See scripts/README.md for the full schema.")
        # signal a data error distinct from a heterogeneity failure
        raise SystemExit(2)

    if len(roles) < 2:
        failures.append(f"Only {len(roles)} role(s); a panel needs at least 2 adaptive voices plus guards.")

    # 1. Pairwise red-line / criteria overlap
    for r1, r2 in combinations(roles, 2):
        rl = jaccard(r1.get("red_line"), r2.get("red_line"))
        cr = jaccard(r1.get("criteria"), r2.get("criteria"))
        if rl >= threshold and cr >= threshold:
            failures.append(
                f"MERGE: '{r1['name']}' and '{r2['name']}' share BOTH red line "
                f"(overlap {rl:.2f}) and criteria (overlap {cr:.2f}) >= {threshold}. "
                f"They are likely one role — merge or regenerate."
            )
        elif rl >= threshold or cr >= threshold:
            which = "red line" if rl >= threshold else "criteria"
            warnings.append(
                f"WATCH: '{r1['name']}' and '{r2['name']}' share {which} "
                f"(overlap {max(rl, cr):.2f}). Acceptable only if the other axis truly differs."
            )

    # 2. Veto-reason test: identical veto reasons across 3+ roles => pseudo-diversity
    veto_groups = {}
    for r in roles:
        v = r.get("veto_reason")
        if v:
            key = frozenset(tokens(v))
            veto_groups.setdefault(key, []).append(r["name"])
    for names in veto_groups.values():
        if len(names) >= 3:
            failures.append(
                f"VETO-REASON: roles {names} would veto for the same reason — "
                f"pseudo-diversity. Regenerate at least two with structurally different stakes."
            )

    # 3. Mandatory paradigm outsider present
    if not any(r.get("is_outsider") for r in roles):
        failures.append("MISSING OUTSIDER: no role flagged is_outsider. At least one paradigm outsider is mandatory.")

    # 4. Adversary roster review must NAME a shared assumption (process gate)
    rr = roster.get("roster_review", {})
    named = rr.get("shared_assumption_named")
    if not named:
        failures.append(
            "EMPTY ROSTER REVIEW: the adversary must name one assumption no role would "
            "challenge (or explicitly state 'none found, and here is why'). "
            "Marking heterogeneity pass without naming the checked assumption is theater."
        )

    return failures, warnings


def main():
    # Windows consoles default to a legacy code page (e.g. cp936) that mojibakes
    # non-ASCII output; force UTF-8 so Chinese role names print correctly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Mechanized heterogeneity check for the advisor panel.")
    ap.add_argument("roster", help="Path to roster JSON")
    ap.add_argument("--threshold", type=float, default=0.6,
                    help="Token-overlap threshold for red-line/criteria collision (default 0.6)")
    args = ap.parse_args()

    try:
        with open(args.roster, encoding="utf-8-sig") as f:
            roster = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR reading roster: {e}", file=sys.stderr)
        return 2

    failures, warnings = check(roster, args.threshold)

    for w in warnings:
        print(f"[warn] {w}")
    if failures:
        print(f"\nHETEROGENEITY CHECK FAILED ({len(failures)} issue(s)):")
        for i, fmsg in enumerate(failures, 1):
            print(f"  {i}. {fmsg}")
        print("\nRegenerate the roster before proceeding to construction.")
        return 1

    print("Heterogeneity check PASSED.")
    print("Note: token overlap is a cheap signal, not proof of genuine difference. "
          "A single model's roles still share a prior — anchor to external evidence "
          "and remember same-model agreement is not correctness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
