#!/usr/bin/env python3
"""Mechanical skill eval: infer routing policy from SKILL.md + optional routing.json,
simulate facilitator decisions on eval tasks, score against assertions, run packaged
script fixtures. Same-model role-play is not used as a score."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN_TASKS = ROOT / "evals" / "tasks.json"
TRAIN_FIXTURES = ROOT / "evals" / "fixtures"


def locate_tasks(skill_dir: Path) -> Path:
    for p in (
        skill_dir / "evals" / "evals.json",
        skill_dir / "evals" / "tasks.json",
        TRAIN_TASKS,
    ):
        if p.is_file():
            return p
    raise FileNotFoundError("no evals.json/tasks.json found")


def locate_fixtures(skill_dir: Path) -> Path:
    for p in (
        skill_dir / "evals" / "fixtures",
        TRAIN_FIXTURES,
    ):
        if p.is_dir():
            return p
    raise FileNotFoundError("no eval fixtures directory found")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def infer_policy(skill_dir: Path) -> dict:
    routing = skill_dir / "routing.json"
    if routing.is_file():
        pol = json.loads(read(routing))
        pol["source"] = "routing.json"
        return pol

    text = read(skill_dir / "SKILL.md")
    always_read = []
    if re.search(r"read at least[`\s]+references/role-generation\.md", text):
        always_read.append("role-generation.md")
    if "read at least" in text and "facilitation.md" in text:
        always_read.append("facilitation.md")

    depth_standard = bool(re.search(r"Default to \*\*Standard\*\*|Default to Standard", text))
    full_posture = bool(
        re.search(r"Full, evidence-grounded", text)
        or re.search(r"By default it runs in full", text)
        or re.search(r"runs in full:", text)
    )
    if full_posture and depth_standard:
        default_depth = "conflict_full"
    elif full_posture:
        default_depth = "full"
    elif depth_standard:
        default_depth = "standard"
    else:
        default_depth = "unspecified"

    phase_gated = bool(
        re.search(r"phase-gated|open .* only if|read-when", text, re.I)
        and "read at least" not in text
    )
    # original has "read at least" so phase_gated is False even if some phase text exists

    return {
        "source": "inferred",
        "default_depth": default_depth,
        "always_read_refs": always_read,
        "phase_gated": phase_gated,
        "ceilings": {
            "minimal": {"max_agents": 0, "max_refs": 0},
            "standard": {"max_agents": 8 if default_depth in ("full", "conflict_full") else 4, "max_refs": max(2, len(always_read))},
            "full": {"max_agents": 8, "max_refs": 6},
        },
        "can_reject": bool(re.search(r"Two-question rejection gate|Chaos check", text)),
        "has_handoff": bool(re.search(r"refuse-and-route|Sibling handoff|skill-handoff", text, re.I)),
        "same_model_supervisor": "forbidden"
        if re.search(r"same-model supervisor.*forbidden|supervisor agent is forbidden", text, re.I)
        else "unspecified",
        "generated_tools": "full_only_disposable"
        if re.search(r"Generated tools.*Full-only|generated helpers are.*deleted", text, re.I)
        else "unspecified",
        "mid_run_adapt": bool(re.search(r"Adapt gate after Phase", text))
        and not bool(re.search(r"no mid-run Adapt|Do not Adapt mid", text, re.I)),
        "closed_menu": bool(re.search(r"closed (enum|menu)|selects from a closed", text, re.I)),
        "guards_non_optional": "adversary" in text.lower() and "never optional" in text.lower(),
        "evals_present": (skill_dir / "evals" / "evals.json").is_file()
        or (skill_dir / "evals" / "tasks.json").is_file(),
        "has_ceiling_table": bool(re.search(r"max_agents|Ceiling", text)),
        "depth_unambiguous": default_depth not in ("conflict_full", "unspecified"),
        "execute_means_scripts_not_full_depth": bool(
            re.search(r"EXECUTE \(scripts|depth defaults to Standard|Full depth is opt-in", text)
        ),
    }


def simulate(policy: dict, task: dict) -> dict:
    kind = task["kind"]
    out = {
        "action": "proceed",
        "depth": "standard",
        "agents": 0,
        "refs": [],
        "six_phase": False,
        "triage": False,
        "guards": False,
        "outsider": False,
        "run_packaged_scripts": False,
        "wall_per_person": False,
        "interest_heavy_lint": False,
        "emit_hddm_sample_code": False,
        "absorb_domain_files": False,
        "generates_supervisor_agent": False,
        "writes_skill_tree_script": False,
        "guards_listed": False,
        "skipped_checks_named": False,
        "method": None,
        "invents_new_process": False,
        "mid_run_adapt": False,
        "selects_from_closed_menu": False,
    }

    def refs_for(depth: str) -> list:
        if policy.get("phase_gated"):
            if depth == "minimal":
                return []
            if depth == "standard":
                return ["role-generation.md"][: policy["ceilings"]["standard"]["max_refs"]]
            return ["role-generation.md", "facilitation.md", "retrieval-and-evidence.md"][
                : policy["ceilings"]["full"]["max_refs"]
            ]
        if depth == "minimal":
            return []
        return list(policy.get("always_read_refs") or [])

    def agents_for(depth: str) -> int:
        return int(policy.get("ceilings", {}).get(depth, {}).get("max_agents", 4))

    if kind.startswith("reject"):
        if policy.get("can_reject"):
            out["action"] = "reject"
            out["agents"] = 0
            out["refs"] = []
            out["six_phase"] = False
            out["triage"] = kind == "reject_chaos"
        else:
            out["action"] = "proceed"
            out["six_phase"] = True
            out["agents"] = agents_for("full")
            out["refs"] = refs_for("full")
        return out

    if kind == "handoff_hddm":
        if policy.get("has_handoff"):
            out["action"] = "handoff"
            out["emit_hddm_sample_code"] = False
            out["absorb_domain_files"] = False
            out["agents"] = 0
            out["refs"] = []
        else:
            out["action"] = "proceed"
            out["depth"] = "full" if policy.get("default_depth") in ("full", "conflict_full") else "standard"
            out["six_phase"] = True
            out["emit_hddm_sample_code"] = True
            out["absorb_domain_files"] = True
            out["agents"] = agents_for(out["depth"])
            out["refs"] = refs_for(out["depth"])
        return out

    if kind == "refuse_supervisor":
        forbidden = policy.get("same_model_supervisor") == "forbidden"
        tools_off = policy.get("generated_tools") in ("full_only_disposable", "off")
        out["action"] = "proceed"
        out["generates_supervisor_agent"] = not forbidden
        out["writes_skill_tree_script"] = not tools_off
        out["guards"] = policy.get("guards_non_optional", False)
        out["outsider"] = True
        return out

    if kind == "refuse_adapt":
        out["action"] = "proceed"
        out["invents_new_process"] = not policy.get("closed_menu")
        out["mid_run_adapt"] = bool(policy.get("mid_run_adapt"))
        out["selects_from_closed_menu"] = bool(policy.get("closed_menu"))
        return out

    if kind == "relaxed_minimal":
        out["action"] = "proceed"
        out["depth"] = "minimal"
        out["agents"] = agents_for("minimal")
        out["refs"] = refs_for("minimal")
        out["six_phase"] = False
        out["guards_listed"] = policy.get("guards_non_optional", False)
        out["skipped_checks_named"] = bool(policy.get("phase_gated") or policy.get("has_ceiling_table"))
        out["guards"] = True
        out["outsider"] = True
        return out

    # proceed_rfc / proceed_interest / proceed_org
    depth = "standard"
    if policy.get("default_depth") in ("full", "conflict_full"):
        depth = "full"
    if policy.get("execute_means_scripts_not_full_depth"):
        depth = "standard"
    out["action"] = "proceed"
    out["depth"] = depth
    out["six_phase"] = True
    out["agents"] = agents_for(depth)
    out["refs"] = refs_for(depth)
    out["guards"] = policy.get("guards_non_optional", False)
    out["outsider"] = True
    out["run_packaged_scripts"] = True
    if kind == "proceed_interest":
        out["wall_per_person"] = True
        out["interest_heavy_lint"] = True
    if kind == "proceed_org":
        out["method"] = "ngt"
    return out


def score_expect(got: dict, expect: dict) -> list:
    hits = []
    for key, want in expect.items():
        if key == "max_agents":
            ok = int(got.get("agents", 99)) <= int(want)
        elif key == "max_refs":
            ok = len(got.get("refs") or []) <= int(want)
        elif key == "max_refs_if_standard":
            if got.get("depth") == "standard":
                ok = len(got.get("refs") or []) <= int(want)
            else:
                ok = False
        elif key == "depth_not_full_by_default":
            ok = got.get("depth") != "full"
        elif key == "not_all_six_refs":
            ok = len(got.get("refs") or []) < 6
        elif key == "no_python_c_inline":
            ok = bool(got.get("run_packaged_scripts"))
        elif key == "six_phase":
            ok = bool(got.get("six_phase")) is bool(want)
        else:
            ok = got.get(key) == want
        hits.append({"key": key, "want": want, "got": got.get(key) if key not in ("max_agents", "max_refs", "max_refs_if_standard", "not_all_six_refs") else (got.get("agents") if "agents" in key else len(got.get("refs") or [])), "ok": ok})
    return hits


def structural_hits(skill_dir: Path, policy: dict) -> list:
    skill = read(skill_dir / "SKILL.md")
    nlines = len(skill.splitlines())
    checks = [
        ("evals_present", policy.get("evals_present", False)),
        ("depth_unambiguous", policy.get("depth_unambiguous", False)),
        ("phase_gated_refs", policy.get("phase_gated", False)),
        ("ceiling_table", policy.get("has_ceiling_table", False)),
        ("handoff", policy.get("has_handoff", False)),
        ("supervisor_forbidden", policy.get("same_model_supervisor") == "forbidden"),
        ("generated_tools_policy", policy.get("generated_tools") in ("full_only_disposable", "off")),
        ("guards_non_optional", policy.get("guards_non_optional", False)),
        ("closed_menu", policy.get("closed_menu", False)),
        ("no_mid_run_adapt", not policy.get("mid_run_adapt", False)),
        ("skill_md_under_500", nlines <= 500),
        ("packaged_scripts_present", all((skill_dir / "scripts" / n).is_file() for n in ("heterogeneity_check.py", "score_options.py", "lint_output.py"))),
        ("execute_not_full_depth", policy.get("execute_means_scripts_not_full_depth", False)),
        ("routing_json", (skill_dir / "routing.json").is_file()),
    ]
    return [{"key": k, "ok": bool(v), "want": True, "got": bool(v)} for k, v in checks]


def run_script(script: Path, args: list) -> dict:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"exit": proc.returncode, "out": (proc.stdout or "") + (proc.stderr or "")}


def script_hits(skill_dir: Path) -> list:
    scripts = skill_dir / "scripts"
    fixtures = locate_fixtures(skill_dir)
    good_roster = fixtures / "good_roster.json"
    bad_roster = fixtures / "bad_roster.json"
    options = fixtures / "options.json"
    good_delib = fixtures / "good_deliberation.md"
    hits = []

    r = run_script(scripts / "heterogeneity_check.py", [str(good_roster)])
    hits.append({"key": "hetero_good_pass", "ok": r["exit"] == 0, "want": 0, "got": r["exit"]})
    r = run_script(scripts / "heterogeneity_check.py", [str(bad_roster)])
    hits.append({"key": "hetero_bad_fail", "ok": r["exit"] == 1, "want": 1, "got": r["exit"]})
    r = run_script(scripts / "score_options.py", [str(options)])
    hits.append({"key": "score_options_runs", "ok": r["exit"] == 0, "want": 0, "got": r["exit"]})
    r = run_script(scripts / "lint_output.py", [str(good_delib), "--interest-heavy"])
    hits.append({"key": "lint_good_pass", "ok": r["exit"] == 0, "want": 0, "got": r["exit"]})
    return hits


def evaluate(skill_dir: Path) -> dict:
    skill_dir = Path(skill_dir)
    tasks = json.loads(read(locate_tasks(skill_dir)))["tasks"]
    policy = infer_policy(skill_dir)
    rows = []
    for task in tasks:
        got = simulate(policy, task)
        hits = score_expect(got, task["expect"])
        rows.append({"id": task["id"], "kind": task["kind"], "hits": hits, "got": got})
    struct = structural_hits(skill_dir, policy)
    scripts = script_hits(skill_dir)
    all_hits = [h for row in rows for h in row["hits"]] + struct + scripts
    passed = sum(1 for h in all_hits if h["ok"])
    total = len(all_hits)
    return {
        "skill_dir": str(skill_dir),
        "policy_source": policy.get("source"),
        "default_depth": policy.get("default_depth"),
        "passed": passed,
        "total": total,
        "score": round(100.0 * passed / total, 2) if total else 0.0,
        "tasks": rows,
        "structural": struct,
        "scripts": scripts,
        "failed": [h for h in all_hits if not h["ok"]],
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) < 2:
        print("usage: simulate_and_score.py <skill_dir> [out.json]")
        return 2
    skill_dir = Path(sys.argv[1])
    result = evaluate(skill_dir)
    print(f"SCORE {result['score']}  {result['passed']}/{result['total']}  depth={result['default_depth']} source={result['policy_source']}")
    fails = result["failed"]
    if fails:
        print(f"FAILED {len(fails)}:")
        for h in fails[:30]:
            print(f"  - {h['key']}: want={h.get('want')} got={h.get('got')}")
    if len(sys.argv) >= 3:
        out = Path(sys.argv[2])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
