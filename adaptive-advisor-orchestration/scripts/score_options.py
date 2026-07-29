#!/usr/bin/env python3
"""
score_options.py — deterministic convergence math for Phase 5.

Models do arithmetic on a scoring matrix unreliably (transcription slips, weight
mistakes, halo effects). This removes that error source: give it the options,
the criteria with weights, and the per-cell scores, and it computes composite
weighted scores or RICE, ranks them, and prints the table. It does NOT decide —
ranking is input to the human Approver, not a verdict.

Input JSON schema (weighted mode):
{
  "mode": "weighted",
  "criteria": [
    {"name": "statistical_integrity", "weight": 0.30},
    {"name": "feasibility", "weight": 0.30},
    ...
  ],
  "options": [
    {"name": "Option A", "scores": {"statistical_integrity": 5, "feasibility": 2, ...}},
    ...
  ]
}

Input JSON schema (RICE mode):
{
  "mode": "rice",
  "options": [
    {"name": "Feature X", "reach": 8000, "impact": 2, "confidence": 0.8, "effort": 5},
    ...
  ]
}

Usage:
  python scripts/score_options.py options.json

Weights need not sum to 1 (they are normalized). Exit 0 on success.
"""
import argparse
import json
import sys


def score_weighted(data):
    criteria = data["criteria"]
    total_w = sum(c["weight"] for c in criteria)
    if total_w <= 0:
        raise ValueError("Criteria weights sum to <= 0.")
    rows = []
    for opt in data["options"]:
        scores = opt.get("scores", {})
        composite = 0.0
        missing = []
        for c in criteria:
            if c["name"] not in scores:
                missing.append(c["name"])
                continue
            composite += scores[c["name"]] * (c["weight"] / total_w)
        rows.append({"name": opt["name"], "composite": composite, "missing": missing})
    rows.sort(key=lambda r: r["composite"], reverse=True)
    return criteria, rows


def score_rice(data):
    rows = []
    for opt in data["options"]:
        try:
            reach = float(opt["reach"])
            impact = float(opt["impact"])
            confidence = float(opt["confidence"])
            effort = float(opt["effort"])
        except (KeyError, ValueError) as e:
            raise ValueError(f"Option '{opt.get('name','?')}' missing/invalid RICE field: {e}")
        if effort <= 0:
            raise ValueError(f"Option '{opt['name']}' has effort <= 0.")
        rice = (reach * impact * confidence) / effort
        rows.append({"name": opt["name"], "composite": rice,
                     "detail": f"({reach:g}*{impact:g}*{confidence:g})/{effort:g}"})
    rows.sort(key=lambda r: r["composite"], reverse=True)
    return rows


def main():
    # Windows consoles default to a legacy code page (e.g. cp936) that mojibakes
    # non-ASCII output; force UTF-8 so Chinese role names print correctly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Deterministic scoring for convergence (Phase 5).")
    ap.add_argument("options", help="Path to options JSON")
    args = ap.parse_args()

    try:
        with open(args.options, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR reading options: {e}", file=sys.stderr)
        return 2

    mode = data.get("mode", "weighted")
    try:
        if mode == "weighted":
            criteria, rows = score_weighted(data)
            wtot = sum(c["weight"] for c in criteria)
            print("Weighted multi-criteria (weights normalized):")
            print("  " + "  ".join(f"{c['name']}({c['weight']/wtot:.2f})" for c in criteria))
            print()
            for i, r in enumerate(rows, 1):
                flag = f"  [!] missing: {r['missing']}" if r["missing"] else ""
                print(f"  {i}. {r['name']:<28} composite = {r['composite']:.3f}{flag}")
        elif mode == "rice":
            rows = score_rice(data)
            print("RICE ranking:")
            for i, r in enumerate(rows, 1):
                print(f"  {i}. {r['name']:<28} RICE = {r['composite']:.1f}   {r['detail']}")
        else:
            print(f"Unknown mode '{mode}'. Use 'weighted' or 'rice'.", file=sys.stderr)
            return 2
    except (KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print("\nThis ranking is input to the human Approver (DACI), not a decision. "
          "Genuine open disagreements must still be preserved, not overridden by the top score.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
