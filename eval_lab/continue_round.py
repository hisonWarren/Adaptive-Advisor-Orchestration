#!/usr/bin/env python3
"""Continue round: repair reduced SKILL, re-probe live routing, promote only if not worse."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from battery import run_battery
from live_routing import probe
from reduce_skill import build_reduced, REDUCED

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "adaptive-advisor-orchestration"
LAB = Path(__file__).resolve().parent
WORK = LAB / "candidates" / "worktree"
MIN_TESTS = 1000


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def copy_skill(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def apply_reduce(dest: Path) -> dict:
    stats = build_reduced(dest)
    src_refs = SKILL / "references"
    dst_refs = dest / "references"
    dst_refs.mkdir(exist_ok=True)
    for p in src_refs.glob("*.md"):
        if not (dst_refs / p.name).exists():
            shutil.copy2(p, dst_refs / p.name)
    return stats


def main() -> int:
    print(f"[continue] {now()}")
    print("[continue] rebuild reduced candidate on a copy of current skill tree")
    copy_skill(WORK)
    stats = apply_reduce(WORK)
    print(f"[continue] reduced chars={stats['chars']} est_tokens={stats['est_tokens']}")

    print("[continue] battery on reduced")
    card = run_battery(WORK)
    print(f"[continue] reduced battery n={card['n']} quality={card['quality']} tokens={card['doc']['est_tokens']}")

    print("[continue] live routing: original vs reduced")
    base_live = probe((SKILL / "SKILL.md").read_text(encoding="utf-8"), "baseline_v2")
    red_live = probe((WORK / "SKILL.md").read_text(encoding="utf-8"), "reduced_v2")
    cmp = {
        "at": now(),
        "baseline_acc": base_live.get("acc"),
        "reduced_acc": red_live.get("acc"),
        "baseline_n": base_live.get("n"),
        "reduced_n": red_live.get("n"),
        "baseline_ok": base_live.get("ok"),
        "reduced_ok": red_live.get("ok"),
        "token_ratio": round(card["doc"]["est_tokens"] / 13752, 4),
        "battery_n": card["n"],
        "battery_quality": card["quality"],
        "misses_baseline": [r for r in (base_live.get("raw") or []) if not r.get("ok")],
        "misses_reduced": [r for r in (red_live.get("raw") or []) if not r.get("ok")],
    }
    (LAB / "reports" / "continue_live_compare.json").write_text(
        json.dumps(cmp, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({k: cmp[k] for k in cmp if k not in ("misses_baseline", "misses_reduced")}, ensure_ascii=False))
    print("[continue] reduced misses:")
    for m in cmp["misses_reduced"]:
        print(" ", m["want"], "got", m["got"], "|", m["prompt"][:70])
    print("[continue] baseline misses:")
    for m in cmp["misses_baseline"]:
        print(" ", m["want"], "got", m["got"], "|", m["prompt"][:70])

    token_ratio = card["doc"]["est_tokens"] / 13752
    live_ok = bool(base_live.get("ok") and red_live.get("ok"))
    live_ge = live_ok and (red_live.get("acc") or 0) + 1e-9 >= (base_live.get("acc") or 0)
    promote = (
        card["n"] >= MIN_TESTS
        and card["quality"] >= 0.99
        and token_ratio <= 0.5
        and live_ge
    )
    reason = (
        f"n={card['n']} quality={card['quality']} tokens={token_ratio:.3f}x "
        f"live {red_live.get('acc')} vs {base_live.get('acc')} => promote={promote}"
    )
    print("[continue]", reason)

    if promote:
        print("[continue] PROMOTION: writing reduced SKILL.md into live skill package")
        apply_reduce(SKILL)
        final = run_battery(SKILL)
        print("[continue] final tokens", final["doc"]["est_tokens"], "hash", final["content_hash"])
    else:
        print("[continue] LOCK HELD — live SKILL.md unchanged")

    report = f"""# Continue round

{now()}

{reason}

Live compare: original acc={base_live.get('acc')} ({base_live.get('n_ok')}/{base_live.get('n')}) vs reduced acc={red_live.get('acc')} ({red_live.get('n_ok')}/{red_live.get('n')})

Reduced misses: {json.dumps(cmp['misses_reduced'], ensure_ascii=False)}
Baseline misses: {json.dumps(cmp['misses_baseline'], ensure_ascii=False)}

Promoted: {promote}
"""
    (LAB / "reports" / "CONTINUE_REPORT.md").write_text(report, encoding="utf-8")
    return 0 if promote else 1


if __name__ == "__main__":
    raise SystemExit(main())
