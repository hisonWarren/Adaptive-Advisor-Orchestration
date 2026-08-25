#!/usr/bin/env python3
"""Unattended optimization loop.

v2 gates may promote if quality does not drop and n>=1000.
reduce_skill is LOCKED until n>=1000 AND quality not worse AND tokens<=50%
AND live routing acc not worse. Gates alone cannot unlock 减负.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from battery import run_battery
from reduce_skill import build_reduced
from live_routing import probe

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "adaptive-advisor-orchestration"
LAB = Path(__file__).resolve().parent
MIN_TESTS = 1000
STATE = LAB / "state" / "loop_state.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"rounds": [], "promoted": [], "rejected": [], "baseline": None, "stop": None}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    (LAB / "reports" / "loop_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def snapshot(tag: str, card: dict) -> Path:
    path = LAB / "baselines" / f"{tag}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def copy_skill(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def install_v2_gates(skill_dir: Path) -> None:
    scripts = skill_dir / "scripts"
    shutil.copy2(LAB / "gates" / "heterogeneity_check_v2.py", scripts / "heterogeneity_check_v2.py")
    shutil.copy2(LAB / "gates" / "lint_output_v2.py", scripts / "lint_output_v2.py")


def quality_not_worse(cand: dict, base: dict) -> bool:
    return cand["quality"] + 1e-9 >= base["quality"] and cand["catch_rate"] + 1e-9 >= base["catch_rate"]


def reduce_allowed(cand: dict, base: dict, live: dict | None) -> tuple[bool, str]:
    if cand["n"] < MIN_TESTS:
        return False, f"n={cand['n']} < {MIN_TESTS}"
    if cand["quality"] + 1e-9 < base["quality"]:
        return False, f"quality {cand['quality']} < baseline {base['quality']}"
    if cand["catch_rate"] + 1e-9 < base["catch_rate"]:
        return False, f"catch_rate {cand['catch_rate']} < baseline {base['catch_rate']}"
    token_ratio = cand["doc"]["est_tokens"] / max(1, base["doc"]["est_tokens"])
    if token_ratio > 0.5:
        return False, f"token_ratio={token_ratio:.3f} > 0.5"
    if not live or not live.get("ok"):
        return False, "no live-model routing delta; 减负 lock held (gates do not measure SKILL.md)"
    if live["reduced_acc"] + 1e-9 < live["baseline_acc"]:
        return False, f"live acc {live['reduced_acc']} < {live['baseline_acc']}"
    if cand["quality"] >= base["quality"] and token_ratio <= 0.5 and live["reduced_acc"] >= live["baseline_acc"]:
        return True, (
            f"quality {cand['quality']}>= {base['quality']}, tokens {token_ratio:.3f}×, "
            f"live {live['reduced_acc']}>= {live['baseline_acc']}, n={cand['n']}"
        )
    return False, "not strictly better"


def apply_reduce(skill_dir: Path) -> None:
    build_reduced(skill_dir)
    src_refs = SKILL / "references"
    dst_refs = skill_dir / "references"
    dst_refs.mkdir(exist_ok=True)
    for p in src_refs.glob("*.md"):
        if not (dst_refs / p.name).exists():
            shutil.copy2(p, dst_refs / p.name)


def render_report(state, baseline, card_a, card_b, final, reduce_ok, reduce_reason, live) -> str:
    return f"""# Adaptive Advisor Orchestration — unattended loop report

Time: {now()}
Pinned skill: v0.3.1
Min tests for 减负: **{MIN_TESTS}**

## Battery

| Run | n | quality | catch_rate | est_tokens | v1 paraphrase false-pass |
|---|---:|---:|---:|---:|---:|
| baseline v0.3.1 | {baseline['n']} | {baseline['quality']} | {baseline['catch_rate']} | {baseline['doc']['est_tokens']} | {baseline['v1_paraphrase_false_pass_rate']} |
| install_v2_gates | {card_a['n']} | {card_a['quality']} | {card_a['catch_rate']} | {card_a['doc']['est_tokens']} | {card_a['v1_paraphrase_false_pass_rate']} |
| reduce candidate | {card_b['n']} | {card_b['quality']} | {card_b['catch_rate']} | {card_b['doc']['est_tokens']} | {card_b['v1_paraphrase_false_pass_rate']} |
| **live tree final** | {final['n']} | {final['quality']} | {final['catch_rate']} | {final['doc']['est_tokens']} | {final['v1_paraphrase_false_pass_rate']} |

## Promotions

- v2 gates: **{'YES — scripts copied beside v1' if state['stop']['v2_promoted'] else 'NO'}**
- reduce SKILL.md: **{'YES' if reduce_ok else 'NO — lock held'}** (`{reduce_reason}`)

## Live routing (capped, not part of the 1000)

{json.dumps(live, ensure_ascii=False, indent=2) if live else 'not run / failed'}

## Known bugs (baseline)

- v1 Jaccard paraphrase false-pass rate: **{baseline['v1_paraphrase_false_pass_rate']}**
- v1 heading-style wall false-fail: **{baseline['v1_heading_wall_false_fail']}**
- v2 catch_rate: **{baseline['catch_rate']}**

## Lock policy (honored)

减负 only if: n≥{MIN_TESTS}, quality ≥ baseline, catch_rate ≥ baseline, tokens ≤ 50%, **and live routing acc ≥ baseline**.
Live `SKILL.md` was {'replaced' if reduce_ok else '**not** replaced'}.

`eval_skill.py` remains document lint. Final stdout: `{final['eval_skill_lint']}`

Hashes: baseline `{baseline['content_hash']}` final `{final['content_hash']}`
"""


def main() -> int:
    t0 = time.time()
    state = load_state()
    print(f"[loop] start {now()} skill={SKILL}")

    print("[loop] Phase 1 — baseline battery on unmodified v0.3.1")
    baseline = run_battery(SKILL)
    snapshot("baseline_v031", baseline)
    state["baseline"] = {
        k: baseline[k]
        for k in ("n", "pass_rate", "quality", "catch_rate", "content_hash", "doc", "v1_paraphrase_false_pass_rate")
    }
    print(
        f"[loop] baseline n={baseline['n']} quality={baseline['quality']} catch={baseline['catch_rate']} "
        f"tokens~{baseline['doc']['est_tokens']} v1_false_pass={baseline['v1_paraphrase_false_pass_rate']}"
    )
    if baseline["n"] < MIN_TESTS:
        state["stop"] = {"reason": "baseline_n_below_min", "n": baseline["n"]}
        save_state(state)
        print("[loop] STOP: baseline n < 1000")
        return 2

    work = LAB / "candidates" / "worktree"
    results = [("baseline", baseline)]

    print("[loop] Phase 2 — candidate install_v2_gates")
    copy_skill(work)
    install_v2_gates(work)
    card_a = run_battery(work)
    snapshot("cand_install_v2", card_a)
    a_ok = quality_not_worse(card_a, baseline) and card_a["n"] >= MIN_TESTS
    rec = {
        "name": "install_v2_gates",
        "promoted": a_ok,
        "quality": card_a["quality"],
        "n": card_a["n"],
        "reason": "quality not worse + n>=1000" if a_ok else "quality drop",
    }
    (state["promoted"] if a_ok else state["rejected"]).append(rec)
    results.append(("install_v2_gates", card_a))
    print(f"[loop] install_v2_gates promoted={a_ok} quality={card_a['quality']}")
    if a_ok:
        install_v2_gates(SKILL)
        print("[loop] PROMOTION: v2 gate scripts copied into skill package (v1 retained)")

    current = run_battery(SKILL) if a_ok else baseline
    snapshot("after_v2", current)

    print("[loop] Phase 3 — reduce_skill candidate (locked)")
    copy_skill(work)
    if a_ok:
        install_v2_gates(work)
    apply_reduce(work)
    card_b = run_battery(work)
    snapshot("cand_reduce_skill", card_b)

    live = {"ok": False}
    print("[loop] Phase 3b — capped live routing probe (8×2 calls)")
    try:
        base_live = probe((SKILL / "SKILL.md").read_text(encoding="utf-8"), "baseline")
        red_live = probe((work / "SKILL.md").read_text(encoding="utf-8"), "reduced")
        live = {
            "ok": bool(base_live.get("ok") and red_live.get("ok")),
            "baseline_acc": base_live.get("acc", 0),
            "reduced_acc": red_live.get("acc", 0),
            "baseline": {k: base_live.get(k) for k in ("n", "acc", "error")},
            "reduced": {k: red_live.get(k) for k in ("n", "acc", "error")},
        }
        snapshot("live_routing", live)
        print(f"[loop] live baseline_acc={live.get('baseline_acc')} reduced_acc={live.get('reduced_acc')} ok={live['ok']}")
    except Exception as e:
        live = {"ok": False, "error": str(e)}
        print(f"[loop] live probe failed: {e}")

    allowed, reason = reduce_allowed(card_b, current, live)
    rec_b = {
        "name": "reduce_skill",
        "promoted": allowed,
        "quality": card_b["quality"],
        "n": card_b["n"],
        "token_ratio": round(card_b["doc"]["est_tokens"] / max(1, current["doc"]["est_tokens"]), 4),
        "reason": reason,
        "live_skill_untouched": not allowed,
    }
    (state["promoted"] if allowed else state["rejected"]).append(rec_b)
    results.append(("reduce_skill", card_b))
    print(f"[loop] reduce_skill promoted={allowed} reason={reason}")
    if allowed:
        apply_reduce(SKILL)
        print("[loop] PROMOTION: reduced SKILL.md written")
    else:
        print("[loop] LOCK HELD: live SKILL.md unchanged")

    final = run_battery(SKILL)
    snapshot("final", final)
    state["final"] = {k: final[k] for k in ("n", "pass_rate", "quality", "catch_rate", "content_hash", "doc")}
    state["live"] = live
    state["stop"] = {
        "reason": "candidates_exhausted",
        "elapsed_s": round(time.time() - t0, 2),
        "reduce_promoted": allowed,
        "v2_promoted": a_ok,
        "min_tests": MIN_TESTS,
        "at": now(),
    }
    state["rounds"] = [
        {
            "name": n,
            "n": c["n"],
            "quality": c["quality"],
            "catch_rate": c["catch_rate"],
            "tokens": c["doc"]["est_tokens"],
            "hash": c["content_hash"],
        }
        for n, c in results
    ]
    save_state(state)
    report = LAB / "reports" / "FINAL_REPORT.md"
    report.write_text(
        render_report(state, baseline, card_a, card_b, final, allowed, reason, live),
        encoding="utf-8",
    )
    print(f"[loop] wrote {report}")
    print(f"[loop] done elapsed={state['stop']['elapsed_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
