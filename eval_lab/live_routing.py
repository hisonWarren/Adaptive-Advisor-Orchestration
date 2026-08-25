#!/usr/bin/env python3
"""Capped live routing probe. Never used as the 1000-test battery."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parent

PROMPTS = [
    ("reject", "Rename this function to foo."),
    ("reject", "Production is down right now. Rollback or hotfix forward?"),
    ("reject", "Standard CRUD app, Postgres or MySQL?"),
    ("reject", "帮我把这段话改得通顺一点。"),
    ("proceed", "High-stakes architecture RFC: split the monolith or not. Tools are available."),
    ("proceed", "Interest-heavy family decision: cohabit with aging parent vs facility. Spouse and teen at home."),
    ("handoff", "dockerHDDM: 100 subjects x 1000 trials, PPC/loglike kernel died. Diagnose and give safe code."),
    ("proceed", "Five-stakeholder org trade-off on a four-day work week."),
    ("reject", "Site is on fire, 500s everywhere. Patch now or roll back?"),
    ("handoff", "HDDM sampling kernel OOM on 80 subjects. Give me working sample code."),
    ("proceed", "RFC: event sourcing vs CRUD for the orders service, two teams disagree."),
    ("reject", "Should a typical blog use MySQL or Postgres?"),
]


def _chat(system: str, user: str, max_tokens: int = 120) -> str:
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
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def parse_action(text: str) -> str:
    m = re.search(r"\{[^{}]*\}", text, re.S)
    if m:
        try:
            obj = json.loads(m.group(0))
            a = str(obj.get("action") or "").lower().strip()
            if a in ("reject", "proceed", "handoff"):
                return a
        except Exception:
            pass
    t = text.lower()
    if "handoff" in t or "sibling" in t:
        return "handoff"
    if any(x in t for x in ("reject", "拒绝", "act first", "do not convene")):
        return "reject"
    return "proceed"


def probe(skill_md: str, label: str) -> dict:
    system = (
        skill_md[:14000]
        + "\n\nYou are the facilitator at Stage 0 only. Reply with ONE JSON object: "
        + '{"action":"reject"|"proceed"|"handoff","depth":"minimal"|"standard"|"full"}'
        + " No other text."
    )
    hits = []
    raw = []
    for want, prompt in PROMPTS:
        try:
            text = _chat(system, prompt)
        except Exception as e:
            return {"ok": False, "error": str(e), "label": label, "n": 0, "acc": 0.0, "raw": raw}
        got = parse_action(text)
        ok = got == want
        hits.append(ok)
        raw.append({"want": want, "got": got, "prompt": prompt, "text": text[:300], "ok": ok})
    acc = sum(hits) / len(hits) if hits else 0.0
    out = {"ok": True, "label": label, "n": len(hits), "acc": round(acc, 4),
           "n_ok": int(sum(hits)), "raw": raw}
    dest = LAB / "reports" / f"live_raw_{label}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1])
    print(json.dumps(probe(p.read_text(encoding="utf-8"), p.stem), ensure_ascii=False, indent=2))
