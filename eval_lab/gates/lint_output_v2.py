#!/usr/bin/env python3
"""lint_output_v2.py — structured wall + deliberation lint. Prose regex is advisory."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_IDENTITY = re.compile(
    r"^(user|users|stakeholder|stakeholders|client|clients|the user|"
    r"用户|来访者|利益相关者|大家|人们)$",
    re.I,
)
EMPTYISH = re.compile(r"^(fine|ok|n/?a|none|无|还好|正常|-)?$", re.I)
GATES = {"pass", "fail", "conditional"}
REQUIRED_FIELDS = ("time_energy", "skill_cognition", "emotion_willingness", "org_constraints")


def check_wall(data: dict, interest_heavy: bool):
    issues, warnings = [], []
    persons = data.get("affected_persons") or []
    if interest_heavy and len(persons) < 2:
        issues.append(f"WALL TOO SMALL: interest-heavy 但只有 {len(persons)} 人，至少 2 个具名真人。")
    gates = []
    for i, p in enumerate(persons):
        tag = p.get("id") or f"#{i}"
        ident = str(p.get("identity") or "").strip()
        if not ident or PLACEHOLDER_IDENTITY.match(ident):
            issues.append(f"WALL PERSON '{tag}': identity={ident!r} 是泛化占位词")
        missing = [f for f in REQUIRED_FIELDS if not str(p.get(f) or "").strip()]
        empty = [f for f in REQUIRED_FIELDS if EMPTYISH.match(str(p.get(f) or "").strip())]
        if missing:
            issues.append(f"WALL PERSON '{tag}': 四类问题缺 {missing}")
        if empty:
            issues.append(f"WALL PERSON '{tag}': 四类问题空壳 {empty}")
        g = str(p.get("gate") or "").strip().lower()
        if g not in GATES:
            issues.append(f"WALL PERSON '{tag}': gate={g!r} 不在 {sorted(GATES)}")
        else:
            gates.append(g)
    if interest_heavy and gates and all(g == "pass" for g in gates):
        warnings.append("SMOOTH WALL: 所有受影响的人都 pass — 现实墙全绿通常意味着没被真正测试")
    return issues, warnings


def lint_markdown(text: str):
    issues, warnings = [], []
    low = text.lower()
    if not re.search(r"verification boundary|验证边界", low):
        issues.append("MISSING SECTION: no Verification Boundary")
    if not re.search(r"honesty|诚实|limitations|局限", low):
        issues.append("MISSING SECTION: no honesty/limitations notes")
    used = set()
    for bracket in re.findall(r"\[E-[^\]]+\]", text):
        used.update(re.findall(r"E-([A-Za-z0-9.\-]+)", bracket))
    defined = set(re.findall(r"(?:\|\s*|^|\s)E-([A-Za-z0-9.\-]+?)\s*(?:\||:|-)", text, re.M))
    for cid in sorted(used):
        if cid not in defined and not re.search(rf"(?<!\[)E-{re.escape(cid)}\b", text):
            issues.append(f"PHANTOM CITATION: [E-{cid}]")
    return issues, warnings


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="deliberation markdown (optional if --wall)")
    ap.add_argument("--wall", help="wall.json")
    ap.add_argument("--interest-heavy", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    issues, warnings = [], []
    if args.path:
        text = Path(args.path).read_text(encoding="utf-8-sig")
        i, w = lint_markdown(text)
        issues, warnings = i, w
    if args.wall:
        data = json.loads(Path(args.wall).read_text(encoding="utf-8-sig"))
        i, w = check_wall(data, args.interest_heavy)
        issues += i
        warnings += w
    elif args.interest_heavy and args.path:
        issues.append("WALL JSON MISSING: --interest-heavy 必须提供 --wall wall.json，禁止从散文正则猜逐人墙")
    for w in warnings:
        print(f"  [warn] {w}")
    if issues:
        print(f"\nOUTPUT LINT FAILED ({len(issues)} issue(s)):")
        for n, msg in enumerate(issues, 1):
            print(f"  {n}. {msg}")
        return 1
    print("Output lint PASSED (v2 structured).")
    return 0


def _self_test() -> int:
    genuine = {
        "interest_heavy": True,
        "affected_persons": [
            {"id": "mother", "identity": "母亲, 78 岁, 行动力下降",
             "time_energy": "每天需协助 4 次", "skill_cognition": "不会用 App",
             "emotion_willingness": "抗拒成为负担, 会隐瞒困难",
             "org_constraints": "养老金上限决定机构方案不可行", "gate": "conditional"},
            {"id": "spouse", "identity": "全职工作的配偶",
             "time_energy": "工作日晚上仅 90 分钟", "skill_cognition": "能用 App 但不愿承担照护调度",
             "emotion_willingness": "已接近倦怠", "org_constraints": "无法再请假", "gate": "fail"},
        ],
    }
    fake = {
        "interest_heavy": True,
        "affected_persons": [
            {"id": "u1", "identity": "user", "time_energy": "fine", "skill_cognition": "ok",
             "emotion_willingness": "fine", "org_constraints": "n/a", "gate": "pass"},
            {"id": "u2", "identity": "stakeholders", "time_energy": "fine", "skill_cognition": "",
             "emotion_willingness": "fine", "org_constraints": "fine", "gate": "pass"},
        ],
    }
    gi, gw = check_wall(genuine, True)
    fi, fw = check_wall(fake, True)
    ok = (not gi) and bool(fi)
    print(f"{'OK ' if not gi else 'BAD'} [genuine] {'PASS' if not gi else 'FAIL'} warnings={len(gw)}")
    print(f"{'OK ' if fi else 'BAD'} [fake] {'FAIL' if fi else 'PASS'} issues={len(fi)} warnings={len(fw)}")
    for msg in fi:
        print(f"     - {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
