#!/usr/bin/env python3
"""Score whether a deliberation answer is usable, not abstract theater."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parent
SKILL = LAB.parent / "adaptive-advisor-orchestration" / "SKILL.md"

PROMPTS = [
    {"id": "family-care", "axis": "interest/family",
     "prompt": "父母 78 岁行动力下降，全职工作的配偶和 14 岁女儿在同一屋檐。是接来同住还是送养老机构？按本 skill Standard 深度给最终回答。不要只谈原则。我要能拿去跟家人开会的一页纸。"},
    {"id": "monolith-rfc", "axis": "domain/architecture",
     "prompt": "6 人团队，订单服务是单体，两名资深工程师主张拆成三个服务，其余人认为会拖垮发布。预算大约 40 万、必须在一个季度内见效。按本 skill Standard 深度给最终回答，我要能在周五例会上拍板。"},
    {"id": "four-day", "axis": "org/calendar",
     "prompt": "公司 80 人，产品、客服、值班 SRE 三方对四天工作制意见冲突。客服怕周末覆盖，SRE 已过载。按本 skill Standard 深度给最终回答。"},
    {"id": "outsource-support", "axis": "interest/labor",
     "prompt": "要把客服外包给第三方。现有 12 人客服团队会裁到 4 人。客户 SLA 是工作日 2 小时响应。按本 skill Standard 深度给最终回答，我要能跟客服主管和 CFO 开会。"},
    {"id": "stripe-vs-inhouse", "axis": "vendor/lock-in",
     "prompt": "核心支付从自建迁到 Stripe。工程想 6 周上线，财务担心汇率、手续费和锁死。国内还有一部分用户走本地渠道。按本 skill Standard 深度给最终回答。"},
    {"id": "pricing-model", "axis": "product/revenue",
     "prompt": "新品定价：销售要统一订阅制好卖，三家大客户坚持按量。ARR 目标 800 万。按本 skill Standard 深度给最终回答，周五要给销售政策。"},
    {"id": "return-to-office", "axis": "org/location",
     "prompt": "强制全员每周回办公室三天。约 25 人已在外地城市定居。工程产出目前不差。按本 skill Standard 深度给最终回答。"},
    {"id": "ship-with-vuln", "axis": "risk/security",
     "prompt": "生产发现中危漏洞（CVSS 6.5），补丁要 5 个工作日。周五必须发版，销售合同周一生效，安全负责人要拦。按本 skill Standard 深度给最终回答。"},
    {"id": "ci-buy-vs-build", "axis": "tooling",
     "prompt": "运维只有 2 人。自建 Jenkins 集群经常坏，有人主张买 GitHub Actions 企业版，有人说锁死 GitHub。按本 skill Standard 深度给最终回答。"},
    {"id": "merge-services", "axis": "architecture/reverse",
     "prompt": "三个小服务（订单查询、库存、通知）一共 2 人维护，事故时排障要跨三个仓库。有人主张合并回单体，有人说开倒车。按本 skill Standard 深度给最终回答。"},
    {"id": "property-transfer", "axis": "family/assets",
     "prompt": "父母名下一套房子，是否过户到我名下。还有一个已婚的哥哥。母亲担心以后看病钱，哥哥觉得过户不公平。按本 skill Standard 深度给最终回答。"},
    {"id": "ai-support-replace", "axis": "labor/automation",
     "prompt": "计划用 AI 客服替代约 30% 一线坐席。客服主管和部分老员工反对，董事会要降本。按本 skill Standard 深度给最终回答。"},
]

ABSTRACT = re.compile(
    r"综合考虑|平衡各方|进一步评估|结合实际情况|值得探讨|可以考虑|"
    r"多方面考量|视情况而定|长期来看|保持开放|建议评估|需要更多信息"
)
DECISION = re.compile(
    r"建议[:：]|推荐[:：]|拍板[:：]|本周|先做|选择[:：]|否决|不拆|同住|机构|维持|试点"
)
PERSON = re.compile(
    r"母亲|父亲|配偶|女儿|哥哥|弟弟|SRE|值班|客服|护士|律师|Approver|"
    r"拍板人|工程师|销售|财务|CFO|主管|坐席|哥哥|子女"
)
OWNER = re.compile(r"Approver|拍板|负责人|CFO|主管|由.{1,16}(做|执行|决定|沟通|签字)")
TRIGGER = re.compile(r"若.{2,60}则|触发|开放项|反转|否则撤回|失败条件|失败则撤回")
NUMBER = re.compile(r"\d")
THEATER = re.compile(r"Phase\s*[0-6]|阶段\s*[0-6]|Preflight|heterogeneity_check")


def score_text(text: str) -> dict:
    head = text[:600]
    hits = {
        "leads_with_answer": bool(DECISION.search(head)),
        "has_number": bool(NUMBER.search(text)),
        "has_named_person": bool(PERSON.search(text)),
        "has_owner": bool(OWNER.search(text)),
        "has_reversal_trigger": bool(TRIGGER.search(text)),
        "not_process_theater_first": not bool(THEATER.search(head[:250])),
        "abstract_filler": bool(ABSTRACT.search(text)),
    }
    if hits["abstract_filler"] and hits["has_number"] and hits["has_owner"]:
        hits["abstract_filler"] = False
    n = sum(1 for k, v in hits.items() if k != "abstract_filler" and v) + (0 if hits["abstract_filler"] else 1)
    return {"hits": hits, "n_ok": n, "total": 7, "score": round(n / 7, 4), "chars": len(text)}


def _chat(system: str, user: str, max_tokens: int = 800) -> str:
    key = os.environ.get("XAI_API_KEY")
    if not key:
        raise RuntimeError("XAI_API_KEY missing")
    body = json.dumps({
        "model": "grok-4.5",
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode()
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def probe(skill_md: str, label: str, resume: bool = True) -> dict:
    dest = LAB / "reports" / f"concreteness_{label}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if resume and dest.exists():
        prev = json.loads(dest.read_text(encoding="utf-8"))
        for r in prev.get("rows") or []:
            if r.get("text"):
                done[r["id"]] = r
        print(f"[resume] {len(done)} cached", flush=True)

    system = (
        skill_md
        + "\n\nHost capabilities (injected): REASONING-ONLY, no sub-agents, no files, no net. "
        "Declare that at the bottom only. Standard depth. Produce the final answer the human can use. "
        "Do not pretend scripts ran."
    )
    rows = []
    for item in PROMPTS:
        if item["id"] in done:
            rows.append(done[item["id"]])
            print(f"[skip] {item['id']} {done[item['id']]['score']}", flush=True)
            continue
        print(f"[call] {item['id']}", flush=True)
        text = _chat(system, item["prompt"])
        scored = score_text(text)
        row = {
            "id": item["id"],
            "axis": item["axis"],
            "score": scored["score"],
            "hits": scored["hits"],
            "chars": scored["chars"],
            "head": text[:500],
            "text": text,
        }
        rows.append(row)
        mean = sum(r["score"] for r in rows) / len(rows)
        partial = {"ok": True, "label": label, "mean": round(mean, 4), "n": len(rows), "rows": rows}
        dest.write_text(json.dumps(partial, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[done] {item['id']} score={scored['score']} mean={mean:.3f} hits={scored['hits']}", flush=True)

    mean = sum(r["score"] for r in rows) / len(rows) if rows else 0.0
    weak = [r["id"] for r in rows if r["score"] < 0.85]
    out = {
        "ok": True, "label": label, "mean": round(mean, 4), "n": len(rows),
        "n_full": sum(1 for r in rows if r["score"] >= 0.85),
        "weak": weak, "rows": rows,
    }
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILL
    label = sys.argv[2] if len(sys.argv) > 2 else "v033_12"
    result = probe(p.read_text(encoding="utf-8"), label)
    summary = {k: result[k] for k in ("label", "mean", "n", "n_full", "weak")}
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    table = LAB / "reports" / "CONCRETENESS_12.md"
    lines = [
        f"# Concreteness 12",
        f"",
        f"label={result['label']} mean={result['mean']} full(>=0.85)={result['n_full']}/{result['n']}",
        f"weak: {', '.join(result['weak']) or 'none'}",
        f"",
        f"| id | axis | score | lead | no-theater | number | person | owner | trigger |",
        f"|---|---|---:|---|---|---|---|---|---|",
    ]
    for r in result["rows"]:
        h = r["hits"]
        def yn(k):
            return "Y" if h[k] else "n"
        lines.append(
            f"| {r['id']} | {r.get('axis','')} | {r['score']} | {yn('leads_with_answer')} | "
            f"{yn('not_process_theater_first')} | {yn('has_number')} | {yn('has_named_person')} | "
            f"{yn('has_owner')} | {yn('has_reversal_trigger')} |"
        )
    table.write_text("\n".join(lines) + "\n", encoding="utf-8")
