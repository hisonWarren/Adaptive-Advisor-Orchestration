#!/usr/bin/env python3
"""Build a reduced SKILL.md candidate. Never writes over the live skill unless loop promotes."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "adaptive-advisor-orchestration"

REDUCED = """---
name: adaptive-advisor-orchestration
description: "Use for decisions with real disagreement: competing domains, conflicting interests, or a seductive answer hiding a trade-off (architecture/RFC, policy, high-risk change, family stakes). Do NOT use for lookups, one-step edits, settled best practice, or emergencies — self-reject those."
license: Proprietary. LICENSE.txt has complete terms
---

# Adaptive Advisor Orchestration

Version: **0.3.3** (gated speaker card)

Let the problem grow its own review team. Permanent anchors: adversary, reality wall, paradigm outsider (rejects native jargon, not the speaker's life / stock persona). Human is Approver.

1. Heterogeneous critique only when red lines differ.
2. Adversary never optional.
3. Final authority stays with the human.
4. Roles are thinking structures, not credentials.

## Quick execution checklist

```
[ ] Preflight FIRST: declare EXECUTE / EXECUTE+NET / REASONING-ONLY / no-subagents (harness-injected)
[ ] Stage 0: exactly one of reject | handoff | proceed
[ ] Phase 1: roster.json -> packaged heterogeneity_check_v2.py (exit 1 => regenerate)
[ ] Phases 2-4: construct, steelman->attack->pre-mortem, reconstruct; wall.json on interest-heavy
[ ] Phase 5-6: numeric rank + Approver slot + honesty notes
[ ] EXECUTE: run packaged scripts, show command+exit code; never python -c rewrite
[ ] Fail-closed LAST: fresh-call review of the artifact (not same-context self-audit)
```

**Output depth.** Default to **Standard**. Full is opt-in. EXECUTE (scripts actually run) is not Full depth. Bare invocation = Standard depth + EXECUTE.

| Class | max_agents | max_refs | scripts | when |
|---|---|---|---|---|
| Minimal | 0 | 0 | none required | `relaxed: prioritize speed` |
| Standard | 4 | 1 | heterogeneity_check_v2 + lint_output_v2 | default |
| Full | 8 | 3 | all three | high stakes or user asks Full |

`max_agents` = concurrent sub-agents. `voices` = role count. One agent may carry several voices. `max_refs` is an **upper bound, not a quota**. Read-when priority if over bound: `facilitation.md` > `role-generation.md` > `retrieval-and-evidence.md`; skip the rest and list skips.

Same-model supervisor agent is forbidden. Generated tools Full-only, disposable, deleted after the run. Closed menu; no mid-run Adapt.

## Execution contract

Preflight is mandatory and copied into the output. Capabilities come from the host, not self-assessment.

Fail-closed: in EXECUTE, missing packaged script log, inline `python -c`, or unanchored load-bearing claim => INVALID. Repair in a **new** call that treats the draft as a stranger's artifact. In REASONING-ONLY, valid requires the label, confidence downgrade, and `prior-only -- unverified` list.

## Stage 0 · Problem qualification

Write the problem in <=300 words, then pick **exactly one**: `reject` | `handoff` | `proceed`.

**reject** when any hold:
- trivial one-step edit / rewrite / rename (e.g. "rename this function to foo", "把这段话改通顺")
- settled best practice and low risk (e.g. standard CRUD Postgres vs MySQL)
- chaos: production down, outage, rollback-or-hotfix-now, closing decision window — act first, do not convene

Two-question rejection gate: (1) recognized best practice exists? (2) risk and uncertainty both low? Both yes -> reject.

**handoff** (refuse-and-route) when the ask is a domain pipeline that already has a skill:
- dockerHDDM / HDDM / PPC kernel died / trial-level DDM fit -> action=handoff; do not emit `model.sample` code
- methodology review / write the paper / submission pipeline -> action=handoff to the paper skill
- no sibling -> stay

**proceed** only when there is real disagreement (architecture RFC, org/family trade-off, high-risk change). Speaker card (gated): first-person/public deliverable only; otherwise `situated: unspecified`.

## Permanent guards (existence; details in references/guards-runbook.md)

Adversary, reality wall, paradigm outsider are never optional. Interest-heavy walls write `wall.json` (>=2 named persons, four load classes). Outsider's axis must not match insiders.

## Required artifacts

- `roster.json` with `criterion_axis`, `role_kind`, `veto_condition` `{metric,direction,threshold}`
- `wall.json` when interest-heavy
- packaged scripts only: `python scripts/heterogeneity_check_v2.py roster.json` and `python scripts/lint_output_v2.py out.md --wall wall.json --interest-heavy`

## Minimum delivery

Preflight state; substrate used; script run log; gate status; fail-closed verdict; verification boundary; honesty notes (same-model agreement is not evidence).

## Final answer (hard)

The human came for a decision they can use this week, not a seminar.

**First 5 lines — before any Preflight / Stage / Phase heading:**
1. 建议: a named option (not 方案A/B, not "it depends")
2. 本周动作: who does what by when
3. 代价: one number (money, hours, people, or a concrete failure)
4. 失败则撤回: an observable trigger
5. Approver 可签字的一句 yes/no

Preflight is **one line at the bottom**, not the opening. Standard depth: no Phase 0-6 headings, no roster tables unless the user asked Full.

These phrases are INVALID unless immediately followed by a number and an owner: 综合考虑, 平衡各方, 进一步评估, 结合实际情况, 可以考虑, 视情况而定, 值得探讨. Rewrite until the five lines exist.

Wall names real people (母亲 / 配偶 / 值班 SRE), never 用户. Adversary: one unpatchable attack in one paragraph, not a risk laundry list.

## References (phase-gated / read-when, not always-read)

- `references/contract-details.md` — full prior execution contract, honesty discipline, anti-patterns
- `references/guards-runbook.md` — four wall questions, pre-mortem
- `references/role-generation.md` — axis selection
- `references/facilitation.md` — only if panel size >= 4
- `references/retrieval-and-evidence.md` — only EXECUTE+NET load-bearing claims
- `references/execution-substrate.md` — sub-agents
- `references/skill-handoff.md` — sibling domain
- `references/worked-examples.md` — calibration
"""

DETAILS_STUB = """# Contract details (advisory unless a gate script checks it)

Moved out of SKILL.md to keep the always-loaded body under the token budget.
Hard constraints remain in SKILL.md and in eval_lab/contract.json.

Former sections live here: Execution contract prose, Heterogeneity protocol,
Six-phase workflow, Honesty discipline (7), Anti-patterns (19), Output format Tn.m.
"""


def build_reduced(dest_skill: Path) -> dict:
    dest_skill.mkdir(parents=True, exist_ok=True)
    (dest_skill / "SKILL.md").write_text(REDUCED, encoding="utf-8")
    refs = dest_skill / "references"
    refs.mkdir(exist_ok=True)
    (refs / "contract-details.md").write_text(DETAILS_STUB, encoding="utf-8")
    return {
        "chars": len(REDUCED),
        "lines": len(REDUCED.splitlines()),
        "est_tokens": len(REDUCED) // 3,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_reduced(Path("/tmp/reduced-skill-preview")), indent=2))
