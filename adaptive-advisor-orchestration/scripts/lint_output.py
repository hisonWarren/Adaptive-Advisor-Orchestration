#!/usr/bin/env python3
"""
lint_output.py — enforce the output discipline the model tends to fake.

The skill's honesty rule is that structure must be present, not performed. This
linter parses a finished deliberation (markdown, numbered-issue skeleton) and
flags the specific omissions the model waves through: consequential claims with
no evidence anchor, phantom [E-...] citations, a missing verification boundary or
honesty section, and — on interest-heavy problems — a reality wall that was not
run per person. It cannot judge whether the CONTENT is good; it enforces that the
scaffolding the skill requires actually exists.

Checks:
  - Every [E-Tn.m-k] citation used in the body is defined in an evidence ledger
    (a line matching '| E-Tn.m-k |' or 'E-Tn.m-k :' / 'E-Tn.m-k -').
  - No conclusion line ('结论' / 'Conclusion:') asserting a consequential claim
    is left with neither an [E-...] anchor nor an explicit 'prior-only' tag.
  - Required sections are present: verification boundary, honesty/limits.
  - If flagged --interest-heavy, the reality wall shows >=2 distinct per-person
    load tests.

Usage:
  python scripts/lint_output.py deliberation.md
  python scripts/lint_output.py deliberation.md --interest-heavy

Exit 0 = clean, 1 = issues found. Advisory: a clean lint means the structure is
present, NOT that the reasoning is correct.
"""
import argparse
import re
import sys


# Match any [E-...] bracket, which may contain one or several comma-separated ids,
# e.g. [E-T1.1-1] or [E-T1.1-1, E-C3]. ANY_CITE detects presence on a line;
# CITE_ID pulls out every individual id.
ANY_CITE_RE = re.compile(r"\[E-[^\]]+\]")
CITE_ID_RE = re.compile(r"E-([A-Za-z0-9.\-]+)")
LEDGER_DEF_RE = re.compile(r"(?:\|\s*|^|\s)E-([A-Za-z0-9.\-]+?)\s*(?:\||:|-)", re.MULTILINE)
CONCLUSION_RE = re.compile(r"(结论|conclusion)\s*[:：]", re.IGNORECASE)
PRIOR_ONLY_RE = re.compile(r"prior-?only|仅先验|未验证|unverified", re.IGNORECASE)


def lint(text, interest_heavy):
    issues = []
    warnings = []

    # every id used inside any [E-...] bracket
    used = set()
    for bracket in ANY_CITE_RE.findall(text):
        used.update(CITE_ID_RE.findall(bracket))
    defined = set(LEDGER_DEF_RE.findall(text))
    phantom = set()
    for cid in used:
        # a citation is "defined" if the id appears in a ledger row (i.e. outside
        # the [E-...] bracket form) — count bare occurrences not preceded by '['
        bare = re.findall(rf"(?<!\[)(?<![A-Za-z0-9.\-])E-{re.escape(cid)}\b", text)
        # bare will include the ledger row if present; if the only occurrences are
        # inside brackets, bare is empty
        bare_outside = [b for b in bare]
        if not bare_outside and cid not in defined:
            phantom.add(cid)
    for cid in sorted(phantom):
        issues.append(f"PHANTOM CITATION: [E-{cid}] is cited but never defined in an evidence ledger row.")

    # Conclusions without anchor or prior-only tag
    for m in CONCLUSION_RE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        if not ANY_CITE_RE.search(line) and not PRIOR_ONLY_RE.search(line):
            snippet = line.strip()[:80]
            warnings.append(
                f"UNANCHORED CONCLUSION: '{snippet}...' has no [E-...] anchor and no "
                f"'prior-only — unverified' tag. Anchor it or mark it unverified."
            )

    # Required sections
    low = text.lower()
    if not re.search(r"verification boundary|验证边界", low):
        issues.append("MISSING SECTION: no 'Verification Boundary' — required in every output.")
    if not re.search(r"honesty|诚实|limitations|局限", low):
        issues.append("MISSING SECTION: no honesty/limitations notes — required in every output.")

    # Per-person wall on interest-heavy problems
    if interest_heavy:
        # count distinct per-person markers near the wall
        person_markers = re.findall(r"(真人[甲乙丙丁]|per[- ]person|for\s+the\s+\w+\s*\()", text, re.IGNORECASE)
        if len(set(person_markers)) < 2:
            issues.append(
                "WALL NOT PER-PERSON: interest-heavy problem, but fewer than 2 distinct "
                "per-person load tests found. Collapsing affected people into one 'user' "
                "flattens the real conflict — run the wall once per affected person."
            )

    return issues, warnings


def main():
    # Windows consoles default to a legacy code page (e.g. cp936) that mojibakes
    # non-ASCII output; force UTF-8 so Chinese role names print correctly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Lint a finished deliberation for required structure.")
    ap.add_argument("path", help="Path to the deliberation markdown")
    ap.add_argument("--interest-heavy", action="store_true",
                    help="Require the reality wall to be run per affected person")
    args = ap.parse_args()

    try:
        with open(args.path, encoding="utf-8-sig") as f:
            text = f.read()
    except OSError as e:
        print(f"ERROR reading file: {e}", file=sys.stderr)
        return 2

    issues, warnings = lint(text, args.interest_heavy)

    for w in warnings:
        print(f"[warn] {w}")
    if issues:
        print(f"\nOUTPUT LINT FAILED ({len(issues)} issue(s)):")
        for i, msg in enumerate(issues, 1):
            print(f"  {i}. {msg}")
        return 1

    print("Output lint PASSED: required structure is present.")
    print("Advisory only — a clean lint means the scaffolding exists, NOT that the reasoning is sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
