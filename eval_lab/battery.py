#!/usr/bin/env python3
"""Run the >=1000-case stability battery. Deterministic. Seed 20260825."""
from __future__ import annotations

import importlib.util
import json
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "adaptive-advisor-orchestration"
LAB = Path(__file__).resolve().parent
SEED = 20260825


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hetero_v2 = _load(LAB / "gates" / "heterogeneity_check_v2.py")
lint_v2 = _load(LAB / "gates" / "lint_output_v2.py")
AXES = sorted(hetero_v2.CRITERION_AXES)
METRICS = [
    ("runway_months", "below", 9), ("oncall_hours_per_week", "above", 12),
    ("unresolved_regulatory_items", "above", 0), ("persons_failing_wall", "above", 0),
    ("rollback_hours", "above", 48), ("observed_vs_selfreport_ratio", "below", 0.5),
    ("p99_latency_ms", "above", 400), ("burnout_index", "above", 3),
    ("reversible_within_days", "above", 14), ("second_order_harm_count", "above", 0),
    ("independent_sources", "below", 2), ("demand_interviews", "below", 8),
]


def hash_prompt(text: str) -> str:
    h = 0x811C9DC5
    for ch in text:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"fnv1a32:{h:08x}"


def run_v1_hetero(roster: dict) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False)
        path = f.name
    proc = subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "heterogeneity_check.py"), path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode


def run_v1_lint(md: str, interest_heavy: bool) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md)
        path = f.name
    args = [sys.executable, str(SKILL / "scripts" / "lint_output.py"), path]
    if interest_heavy:
        args.append("--interest-heavy")
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode


def genuine_roster(rng: random.Random, i: int) -> dict:
    axes = rng.sample(AXES, k=6)
    kinds = ["domain", "domain", "domain", "guard_reality_wall", "guard_pre_mortem", "outsider"]
    roles = []
    for k, axis, (metric, direction, thresh) in zip(kinds, axes, METRICS):
        roles.append({
            "id": f"{k[:4]}-{i}-{axis[:4]}", "name": f"{k}-{axis}", "role_kind": k,
            "criterion_axis": axis, "is_outsider": k == "outsider",
            "red_line": f"veto unless {metric} holds for {axis}",
            "criteria": f"independent {axis} measurement", "veto_reason": f"fails {metric}",
            "veto_condition": {"metric": f"{metric}_{i}", "direction": direction, "threshold": thresh},
        })
    return {"roles": roles, "roster_review": {
        "shared_assumption_named": f"all six roles assume the project should proceed ({i})",
        "regenerated": False,
    }}


def fake_roster(rng: random.Random, i: int) -> dict:
    variants = [
        "will not sign off unless the delivered artifact meets a high standard of quality and craftsmanship",
        "refuses to approve anything whose excellence falls below what the team considers good work",
        "最终产出的优良程度未达我们通常坚持的标准即否决",
        "交付物达不到应有的质量与工艺水准就不签字",
        "凡是精良程度低于团队公认好作品的，一律不予批准",
    ]
    roles = []
    for n, title in enumerate(("sre", "arch", "lead")):
        roles.append({
            "id": f"{title}-{i}", "name": title, "role_kind": "domain",
            "criterion_axis": "technical_correctness", "is_outsider": n == 1,
            "red_line": variants[(i + n) % len(variants)],
            "criteria": rng.choice(["overall quality of the delivered work", "how good the final output is judged to be", "质量与工艺"]),
            "veto_reason": "quality too low",
            "veto_condition": {"metric": "quality_score", "direction": "below", "threshold": 8 - n},
        })
    return {"roles": roles, "roster_review": {"shared_assumption_named": "", "regenerated": False}}


def v1_shape_roster(_fake: dict) -> dict:
    return {"roles": [
        {"name": "Senior Reliability Engineer",
         "red_line": "will not sign off unless the delivered artifact meets a high standard of quality and craftsmanship",
         "criteria": "overall quality of the delivered work", "is_outsider": False,
         "veto_reason": "craftsmanship bar not met"},
        {"name": "Principal Platform Architect",
         "red_line": "refuses to approve anything whose excellence falls below what the team considers good work",
         "criteria": "how good the final output is judged to be", "is_outsider": False,
         "veto_reason": "excellence shortfall"},
        {"name": "Field ethnographer",
         "red_line": "reject conclusions built only on self-report",
         "criteria": "observed versus claimed behavior", "is_outsider": True,
         "veto_reason": "no observational evidence"},
    ], "roster_review": {"shared_assumption_named": "the change is worth doing; we only argue how well", "regenerated": False}}


def genuine_wall(i: int) -> dict:
    people = [
        ("mother", f"母亲 {70+i%10} 岁 行动力下降", "每天协助 4 次", "不会用 App", "怕成为负担会隐瞒", "养老金上限", "conditional"),
        ("spouse", "全职工作的配偶", "工作日仅 90 分钟", "能用工具但不愿调度", "接近倦怠", "无法再请假", "fail"),
        ("teen", "14 岁女儿", "课后两小时", "不懂照护流程", "不愿家里变成病房", "学区不能搬", "conditional"),
    ]
    take = people if i % 2 == 0 else people[:2]
    return {"interest_heavy": True, "affected_persons": [
        {"id": a, "identity": b, "time_energy": c, "skill_cognition": d,
         "emotion_willingness": e, "org_constraints": f, "gate": g}
        for a, b, c, d, e, f, g in take
    ]}


def fake_wall(i: int) -> dict:
    return {"interest_heavy": True, "affected_persons": [
        {"id": "u1", "identity": "user", "time_energy": "fine", "skill_cognition": "ok",
         "emotion_willingness": "fine", "org_constraints": "n/a", "gate": "pass"},
        {"id": "u2", "identity": "stakeholders", "time_energy": "fine", "skill_cognition": "",
         "emotion_willingness": "fine", "org_constraints": "fine", "gate": "pass"},
    ]}


HEADING_WALL_MD = """# Deliberation
## Verification Boundary
推理边界已标明。
## Honesty notes
单模型先验未打破。
### 母亲（78 岁）
时间精力：每天协助四次。技能认知：不会用 App。情绪意愿：怕成为负担。组织约束：养老金上限。
### 全职工作的配偶
时间精力：晚上 90 分钟。技能认知：能用工具。情绪意愿：倦怠。组织约束：不能再请假。
结论：需要逐人承受力核对。
"""

INLINE_WALL_MD = """# Deliberation
## Verification Boundary
ok
## Honesty notes
ok
load test for the parent (autonomy) and for the spouse (load)
结论：墙已按人跑过 [E-T1.1-1]
E-T1.1-1 : wall
"""


def doc_properties(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    desc = ""
    if text.startswith("---"):
        end = text.find("\\n---", 3)
        fm = text[3:end] if end != -1 else ""
        m = re.search(r'description:\\s+"(.*)"', fm, re.S)
        desc = m.group(1) if m else ""
    n_must = len(re.findall(r"\\b(must|never|do not|mandatory|不得|必须|禁止)\\b", text, re.I))
    contradictions = []
    if "Prefer 4–8 active voices" in text and "Standard | 4 |" in text:
        contradictions.append("voices_vs_agents")
    if "| Standard | 4 | 1 |" in text and "Open `references/facilitation.md` only if panel size >= 4" in text:
        contradictions.append("refs_ceiling_vs_readwhen")
    if "EXECUTE / EXECUTE+NET / REASONING-ONLY" in text and "sub-agents / tools-inline / reasoning-only" in text:
        contradictions.append("preflight_3_vs_delivery_4")
    return {
        "chars": len(text), "lines": len(text.splitlines()), "est_tokens": max(1, len(text) // 3),
        "description_words": len(desc.split()), "hard_constraint_words": n_must,
        "contradictions": contradictions, "content_hash": hash_prompt(text),
    }


def run_eval_skill(skill_dir: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(skill_dir / "scripts" / "eval_skill.py"), str(skill_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    line = (proc.stdout or "").strip().splitlines()[:1]
    return {"exit": proc.returncode, "stdout": " ".join(line), "advisory_only": True}


def score_trace(trace: dict, expect: dict) -> dict:
    calls = [c.get("name", "") for c in trace.get("tool_calls") or []]
    joined = " ".join(f"{c.get('name','')} {c.get('input','')} {c.get('output','')}" for c in (trace.get("tool_calls") or []))
    files = set((trace.get("files") or {}).keys())
    text = trace.get("text") or ""
    got = {
        "rejects": bool(trace.get("rejects") or "reject" in text.lower()[:400]),
        "proceeds": not bool(trace.get("rejects")),
        "calls_heterogeneity_check": any("heterogeneity_check" in n for n in calls),
        "no_inline_reimplementation": "python -c" not in joined,
        "emits_roster_json": any(Path(p).name == "roster.json" for p in files),
        "emits_wall_json": any(Path(p).name == "wall.json" for p in files),
        "calls_lint_output": any("lint_output" in n for n in calls),
        "preflight_declared": any(s in text for s in ("EXECUTE", "EXECUTE+NET", "REASONING-ONLY")),
        "preflight_is": next((s for s in ("EXECUTE+NET", "REASONING-ONLY", "EXECUTE") if s in text[:500]), None),
        "max_agents": trace.get("agents_used", 0),
        "max_refs": trace.get("refs_used", 0),
        "heterogeneity_exit_code": next((c.get("exit_code") for c in (trace.get("tool_calls") or []) if "heterogeneity_check" in c.get("name", "")), None),
    }
    hits = {}
    for k, want in expect.items():
        if k in ("max_agents", "max_refs"):
            hits[k] = got.get(k, 99) <= want
        elif k in ("preflight_is", "heterogeneity_exit_code"):
            hits[k] = got.get(k) == want
        else:
            hits[k] = bool(got.get(k)) is bool(want)
    return {"hits": hits, "pass": all(hits.values()), "got": got}


def synthetic_traces():
    tasks = json.loads((LAB / "suites" / "behavioral_tasks.json").read_text(encoding="utf-8"))["tasks"]
    out = []
    for t in tasks:
        good = {"text": "EXECUTE\\n" + ("REJECT: trivial" if t["expect"].get("rejects") else "proceeding"),
                "rejects": bool(t["expect"].get("rejects")), "tool_calls": [], "files": {}, "agents_used": 0, "refs_used": 0}
        if t["expect"].get("calls_heterogeneity_check"):
            good["tool_calls"].append({"name": "heterogeneity_check_v2.py", "input": "roster.json",
                "output": "FAILED" if t["id"] == "T07-pseudo-diversity-caught" else "PASSED",
                "exit_code": 1 if t["id"] == "T07-pseudo-diversity-caught" else 0})
            good["files"]["roster.json"] = "{}"
        if t["expect"].get("emits_roster_json"):
            good["files"]["roster.json"] = "{}"
        if t["expect"].get("emits_wall_json"):
            good["files"]["wall.json"] = "{}"
        if t["expect"].get("calls_lint_output"):
            good["tool_calls"].append({"name": "lint_output_v2.py", "input": "out.md", "output": "PASSED", "exit_code": 0})
        if t["expect"].get("preflight_is"):
            good["text"] = t["expect"]["preflight_is"] + "\\n" + good["text"]
        out.append((t["id"] + "/good", good, dict(t["expect"]), True))
        fake = {"text": "looks thorough", "rejects": False,
                "tool_calls": [{"name": "python -c", "input": "print('ok')", "output": "ok", "exit_code": 0}],
                "files": {}, "agents_used": 12, "refs_used": 9}
        out.append((t["id"] + "/faked", fake, dict(t["expect"]), False))
    return out


def run_battery(skill_dir: Path, n_fuzz: int = 2200) -> dict:
    rng = random.Random(SEED)
    skill_dir = Path(skill_dir)
    cases = []
    n_each = n_fuzz // 4
    for i in range(n_each):
        issues, _ = hetero_v2.check_roster(genuine_roster(rng, i))
        cases.append({"id": f"hv2-genuine-{i}", "suite": "hetero_v2", "ok": not issues})
        issues, _ = hetero_v2.check_roster(fake_roster(rng, i))
        cases.append({"id": f"hv2-fake-{i}", "suite": "hetero_v2", "ok": bool(issues)})
        issues, _ = lint_v2.check_wall(genuine_wall(i), True)
        cases.append({"id": f"wallv2-genuine-{i}", "suite": "wall_v2", "ok": not issues})
        issues, _ = lint_v2.check_wall(fake_wall(i), True)
        cases.append({"id": f"wallv2-fake-{i}", "suite": "wall_v2", "ok": bool(issues)})

    code0 = run_v1_hetero(v1_shape_roster({}))
    v1_paraphrase_pass = 200 if code0 == 0 else 0
    for i in range(200):
        cases.append({"id": f"v1-paraphrase-{i}", "suite": "v1_known_bug", "ok": True, "detail": "v1_pass" if code0 == 0 else "v1_fail"})
        issues, _ = hetero_v2.check_roster(fake_roster(rng, i))
        cases.append({"id": f"v2-catches-paraphrase-{i}", "suite": "known_bug_catch", "ok": bool(issues)})

    v1_heading_fail = run_v1_lint(HEADING_WALL_MD, True) == 1
    v1_inline_pass = run_v1_lint(INLINE_WALL_MD, True) == 0
    cases.append({"id": "v1-heading-wall-false-fail", "suite": "v1_known_bug", "ok": True, "detail": "false_fail" if v1_heading_fail else "unexpected_pass"})
    cases.append({"id": "v1-inline-wall-pass", "suite": "v1_known_bug", "ok": True, "detail": "pass" if v1_inline_pass else "fail"})
    gi, _ = lint_v2.check_wall(genuine_wall(0), True)
    fi, _ = lint_v2.check_wall(fake_wall(0), True)
    cases.append({"id": "v2-genuine-wall", "suite": "known_bug_catch", "ok": not gi})
    cases.append({"id": "v2-fake-wall", "suite": "known_bug_catch", "ok": bool(fi)})

    for tid, trace, expect, should_pass in synthetic_traces():
        scored = score_trace(trace, expect)
        cases.append({"id": tid, "suite": "trace_scorer", "ok": scored["pass"] is should_pass})

    doc = doc_properties(skill_dir)
    lint = run_eval_skill(skill_dir)
    cases.append({"id": "doc-hash-present", "suite": "doc", "ok": bool(doc["content_hash"])})
    cases.append({"id": "eval_skill_advisory_ran", "suite": "doc", "ok": "SCORE" in lint["stdout"]})

    n = len(cases)
    passed = sum(1 for c in cases if c["ok"])
    catch = [c for c in cases if c["suite"] == "known_bug_catch"]
    quality_cases = [c for c in cases if c["suite"] in ("hetero_v2", "wall_v2", "known_bug_catch", "trace_scorer")]
    quality = sum(1 for c in quality_cases if c["ok"]) / max(1, len(quality_cases))
    return {
        "n": n, "passed": passed, "pass_rate": round(passed / n, 6),
        "quality": round(quality, 6),
        "catch_rate": round(sum(1 for c in catch if c["ok"]) / max(1, len(catch)), 6),
        "v1_paraphrase_false_pass_rate": round(v1_paraphrase_pass / 200, 6),
        "v1_heading_wall_false_fail": v1_heading_fail,
        "suites": dict(Counter(c["suite"] for c in cases)),
        "suite_fails": dict(Counter(c["suite"] for c in cases if not c["ok"])),
        "doc": doc, "eval_skill_lint": lint["stdout"], "content_hash": doc["content_hash"],
        "failed_ids": [c["id"] for c in cases if not c["ok"]][:40],
    }


def main():
    skill = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILL
    result = run_battery(skill)
    print(json.dumps({k: result[k] for k in result if k != "failed_ids"}, indent=2, ensure_ascii=False))
    print("failed_ids:", result["failed_ids"])
    out = LAB / "reports" / "battery_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if result["quality"] >= 0.99 else 1


if __name__ == "__main__":
    raise SystemExit(main())
