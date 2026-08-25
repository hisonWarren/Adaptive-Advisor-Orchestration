#!/usr/bin/env python3
"""
heterogeneity_check_v2.py — 把异质性判据从"词面重合度"换成"结构化枚举 + 可证伪否决条件"。

原 heterogeneity_check.py 用 Jaccard token 重合度（阈值 0.6）比对 red_line / criteria。
实测缺陷：把 bad_roster 里那对伪多样性角色（两个都只关心"质量"）改写成更啰嗦的
自然措辞，语义完全不变，Jaccard 被稀释后直接 PASS。

    $ python3 scripts/heterogeneity_check.py probe2/paraphrased_roster.json
    Heterogeneity check PASSED.

这是个单向漂移：新模型普遍更啰嗦 → 同一份伪多样性名单的通过率随版本单调上升 →
看起来"变好了"，实际是检测器失效了。

v2 的判据全部落在**枚举与结构**上，措辞怎么写都绕不过去：

  1. criterion_axis 必须是受控枚举，且去重后 ≥3 个轴、单轴占比 ≤50%
  2. veto_condition 必须是 {metric, direction, threshold} 三元组，且 metric 互不相同
  3. 两个硬 guard（reality_wall / pre_mortem）必须在名单里，不可省
  4. outsider 的轴不能与任何内部角色重合
  5. roster_review.shared_assumption_named 必须非空

Jaccard 降级为 warning —— 它仍是有用的廉价信号，只是不再有否决权。

用法:
  python3 heterogeneity_check_v2.py roster.json
  python3 heterogeneity_check_v2.py --self-test

退出码: 0 = 通过, 1 = 有阻断项。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ------------------------------------------------------------------ 受控词表
# 轴 = "这个角色到底在为哪一类可证伪的东西把关"。枚举无法靠改写措辞扩容，
# 这正是它比自由文本可靠的地方。新增轴要改这份表，是一次显式决定。
CRITERION_AXES = {
    "cost",                  # 钱
    "time_schedule",         # 工期 / 时间窗
    "compliance_legal",      # 合规、法律、审计
    "safety_harm",           # 人身 / 心理伤害
    "technical_correctness", # 技术上对不对
    "operational_load",      # 谁来长期扛这摊事
    "emotion_relational",    # 关系与情绪成本
    "reversibility",         # 错了能不能退回来
    "second_order",          # 二阶 / 外部性效应
    "epistemic_validity",    # 证据本身站不站得住
    "market_demand",         # 有没有人真的要
    "equity_distribution",   # 收益与代价怎么分配
}

REQUIRED_GUARDS = {"guard_reality_wall", "guard_pre_mortem"}
ROLE_KINDS = REQUIRED_GUARDS | {"domain", "outsider", "second_order"}

MAX_AXIS_SHARE = 0.5   # 单轴占比上限
MIN_DISTINCT_AXES = 3  # 去重后最少轴数
JACCARD_WARN = 0.6     # 仅 warning

VAGUE_METRIC = re.compile(
    r"^(quality|quality_score|goodness|excellence|overall|score|标准|质量|好坏|水平)$",
    re.IGNORECASE,
)
DIRECTIONS = {"below", "above", "equals", "outside"}


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", str(text).lower()))


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def check_roster(data: dict):
    issues, warnings = [], []
    roles = data.get("roles") or []

    if len(roles) < 3:
        issues.append(f"ROSTER TOO SMALL: 只有 {len(roles)} 个角色，两个硬 guard 之外至少还要 1 个实质角色。")

    # ---- 1. 轴：枚举合法性 + 覆盖度 + 集中度
    axes = []
    for i, r in enumerate(roles):
        tag = r.get("id") or r.get("name") or f"#{i}"
        axis = r.get("criterion_axis")
        if axis not in CRITERION_AXES:
            issues.append(
                f"BAD AXIS: 角色 '{tag}' 的 criterion_axis={axis!r} 不在受控词表里。"
                f"合法值：{sorted(CRITERION_AXES)}"
            )
            continue
        axes.append(axis)

    distinct = sorted(set(axes))
    if axes and len(distinct) < MIN_DISTINCT_AXES:
        issues.append(
            f"PSEUDO-DIVERSITY: {len(roles)} 个角色只覆盖 {len(distinct)} 个判据轴 {distinct}。"
            f"至少需要 {MIN_DISTINCT_AXES} 个不同的轴 —— 换措辞不算换判据。"
        )
    if axes:
        for axis, n in Counter(axes).most_common():
            share = n / len(axes)
            if share > MAX_AXIS_SHARE:
                issues.append(
                    f"AXIS DOMINATED: '{axis}' 占了 {share:.0%} 的角色（上限 {MAX_AXIS_SHARE:.0%}）。"
                    "一群人换着说法关心同一件事，不是异质性。"
                )

    # ---- 2. 否决条件：必须可证伪，且互不共享 metric
    metric_owners = {}
    for i, r in enumerate(roles):
        tag = r.get("id") or r.get("name") or f"#{i}"
        veto = r.get("veto_condition")
        if not isinstance(veto, dict):
            issues.append(
                f"VETO NOT FALSIFIABLE: 角色 '{tag}' 的 veto_condition 不是 "
                "{metric, direction, threshold} 三元组。散文式否决权等于没有否决权。"
            )
            continue
        metric = str(veto.get("metric") or "").strip()
        direction = str(veto.get("direction") or "").strip().lower()
        threshold = veto.get("threshold")
        if not metric:
            issues.append(f"VETO NOT FALSIFIABLE: 角色 '{tag}' 的 veto metric 为空。")
        elif VAGUE_METRIC.match(metric):
            issues.append(
                f"VETO VAGUE METRIC: 角色 '{tag}' 的 metric='{metric}' 是笼统词。"
                "否决条件必须指向一个能独立测量的量。"
            )
        if direction not in DIRECTIONS:
            issues.append(f"VETO NOT FALSIFIABLE: 角色 '{tag}' 的 direction={direction!r} 不在 {sorted(DIRECTIONS)}。")
        if threshold in (None, "", []):
            issues.append(f"VETO NOT FALSIFIABLE: 角色 '{tag}' 没写 threshold，条件无法判真假。")
        if metric:
            metric_owners.setdefault(metric.lower(), []).append(tag)

    for metric, owners in metric_owners.items():
        if len(owners) > 1:
            issues.append(
                f"VETO COLLAPSE: 角色 {owners} 的否决条件都盯着同一个 metric '{metric}'。"
                "他们的否决权是同一份，不是两份。"
            )

    # ---- 3. 两个硬 guard 不可省
    kinds = set()
    for i, r in enumerate(roles):
        kind = r.get("role_kind")
        if kind is not None and kind not in ROLE_KINDS:
            issues.append(f"BAD ROLE KIND: 角色 '{r.get('id', i)}' 的 role_kind={kind!r} 不在 {sorted(ROLE_KINDS)}。")
        kinds.add(kind)
    for guard in sorted(REQUIRED_GUARDS):
        if guard not in kinds:
            issues.append(f"MISSING GUARD: 名单里没有 role_kind='{guard}'。两个硬 guard 不可省。")

    # ---- 4. outsider 必须真的在别的轴上
    insider_axes = {
        r.get("criterion_axis")
        for r in roles
        if not r.get("is_outsider") and r.get("role_kind") not in REQUIRED_GUARDS
    }
    outsiders = [r for r in roles if r.get("is_outsider")]
    if not outsiders:
        issues.append("MISSING OUTSIDER: 名单里没有 is_outsider=true 的角色。至少要有一个范式外的人。")
    for r in outsiders:
        tag = r.get("id") or r.get("name") or "?"
        if r.get("criterion_axis") in insider_axes:
            issues.append(
                f"FAKE OUTSIDER: '{tag}' 的轴 '{r.get('criterion_axis')}' 已被内部角色占用。"
                "换个头衔不等于换个范式。"
            )

    # ---- 5. 名单自审：共享假设必须被显式写出来
    review = data.get("roster_review") or {}
    shared = str(review.get("shared_assumption_named") or "").strip()
    if not shared:
        issues.append("MISSING ROSTER REVIEW: 必须显式写出这批角色共享的那条假设 —— 没写通常等于没找。")
    elif len(shared) < 12:
        warnings.append(f"THIN ROSTER REVIEW: shared_assumption_named='{shared}' 过短，像是应付字段。")

    # ---- warning 层：Jaccard 保留但无否决权
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            a, b = roles[i], roles[j]
            score = _jaccard(a.get("red_line", ""), b.get("red_line", ""))
            if score >= JACCARD_WARN:
                warnings.append(
                    f"WORDING OVERLAP: '{a.get('id', i)}' 与 '{b.get('id', j)}' 的 red_line 词面重合 {score:.2f}。"
                    "仅供参考 —— 判定以轴与否决条件为准。"
                )

    warnings.append(
        "SAME-MODEL PRIOR: 这批角色由同一个模型生成，共享同一份先验。"
        "结构上的异质不等于认识论上的独立 —— 载重结论仍需外部证据。"
    )
    return issues, warnings


# ------------------------------------------------------------------ 自检
GENUINE = {
    "roles": [
        {"id": "cfo", "role_kind": "domain", "criterion_axis": "cost", "is_outsider": False,
         "red_line": "现金流断裂前不批",
         "veto_condition": {"metric": "runway_months", "direction": "below", "threshold": 9}},
        {"id": "ops", "role_kind": "domain", "criterion_axis": "operational_load", "is_outsider": False,
         "red_line": "没人长期扛这摊事就不批",
         "veto_condition": {"metric": "oncall_hours_per_week", "direction": "above", "threshold": 12}},
        {"id": "counsel", "role_kind": "domain", "criterion_axis": "compliance_legal", "is_outsider": False,
         "red_line": "监管口径未明前不批",
         "veto_condition": {"metric": "unresolved_regulatory_items", "direction": "above", "threshold": 0}},
        {"id": "wall", "role_kind": "guard_reality_wall", "criterion_axis": "emotion_relational", "is_outsider": False,
         "red_line": "任一受影响的人 gate=fail 就不批",
         "veto_condition": {"metric": "persons_failing_wall", "direction": "above", "threshold": 0}},
        {"id": "premortem", "role_kind": "guard_pre_mortem", "criterion_axis": "reversibility", "is_outsider": False,
         "red_line": "失败后退不回来就不批",
         "veto_condition": {"metric": "rollback_hours", "direction": "above", "threshold": 48}},
        {"id": "ethnographer", "role_kind": "outsider", "criterion_axis": "epistemic_validity", "is_outsider": True,
         "red_line": "结论只建立在自我报告上就不批",
         "veto_condition": {"metric": "observed_vs_selfreport_ratio", "direction": "below", "threshold": 0.5}},
    ],
    "roster_review": {
        "shared_assumption_named": "六个角色都默认这件事值得做，只在怎么做上分歧；没有人负责论证不做",
        "regenerated": True,
    },
}

# 上一轮实测中 v1 判 PASS 的那份同义改写名单 —— v2 必须判 FAIL
PARAPHRASED_FAKE = {
    "roles": [
        {"id": "sre", "role_kind": "domain", "criterion_axis": "technical_correctness", "is_outsider": False,
         "red_line": "交付物达不到应有的质量与工艺水准就不签字",
         "veto_condition": {"metric": "quality_score", "direction": "below", "threshold": 8}},
        {"id": "arch", "role_kind": "domain", "criterion_axis": "technical_correctness", "is_outsider": True,
         "red_line": "凡是精良程度低于团队公认好作品的，一律不予批准",
         "veto_condition": {"metric": "quality_score", "direction": "below", "threshold": 7}},
        {"id": "lead", "role_kind": "domain", "criterion_axis": "technical_correctness", "is_outsider": False,
         "red_line": "最终产出的优良程度未达我们通常坚持的标准即否决",
         "veto_condition": {"metric": "quality_score", "direction": "below", "threshold": 9}},
    ],
    "roster_review": {"shared_assumption_named": "", "regenerated": False},
}


def self_test() -> int:
    ok = True
    for label, data, want_pass in (("genuine", GENUINE, True), ("paraphrased_fake", PARAPHRASED_FAKE, False)):
        issues, warnings = check_roster(data)
        passed = not issues
        mark = "OK " if passed == want_pass else "BAD"
        ok = ok and (passed == want_pass)
        print(f"{mark} [{label}] {'PASS' if passed else f'FAIL ({len(issues)} 项)'}  warnings={len(warnings)}")
        for msg in issues:
            print(f"     - {msg}")
    print("\n自检要点：paraphrased_fake 是 v1 判 PASS 的那份同义改写名单，v2 必须判 FAIL。")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roster", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.roster:
        ap.error("需要 roster.json 路径，或用 --self-test")

    data = json.loads(Path(args.roster).read_text(encoding="utf-8-sig"))
    issues, warnings = check_roster(data)
    for w in warnings:
        print(f"  [warn] {w}")
    if issues:
        print(f"\nHETEROGENEITY CHECK FAILED ({len(issues)} issue(s)):")
        for n, msg in enumerate(issues, 1):
            print(f"  {n}. {msg}")
        return 1
    print("Heterogeneity check PASSED：轴覆盖、否决条件、guard、outsider、名单自审齐备。")
    print("仍是 advisory —— 结构异质不等于认识论独立。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
