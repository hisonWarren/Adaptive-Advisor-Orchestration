# Adaptive Advisor Orchestration — unattended loop report

Time: 2026-08-25T05:56:02.218565+00:00
Pinned skill: v0.3.1
Min tests for 减负: **1000**

## Battery

| Run | n | quality | catch_rate | est_tokens | v1 paraphrase false-pass |
|---|---:|---:|---:|---:|---:|
| baseline v0.3.1 | 2630 | 1.0 | 1.0 | 13752 | 1.0 |
| install_v2_gates | 2630 | 1.0 | 1.0 | 13752 | 1.0 |
| reduce candidate | 2630 | 1.0 | 1.0 | 1498 | 1.0 |
| **live tree final** | 2630 | 1.0 | 1.0 | 13752 | 1.0 |

## Promotions

- v2 gates: **YES — scripts copied beside v1**
- reduce SKILL.md: **NO — lock held** (`live acc 0.875 < 1.0`)

## Live routing (capped, not part of the 1000)

{
  "ok": true,
  "baseline_acc": 1.0,
  "reduced_acc": 0.875,
  "baseline": {
    "n": 8,
    "acc": 1.0,
    "error": null
  },
  "reduced": {
    "n": 8,
    "acc": 0.875,
    "error": null
  }
}

## Known bugs (baseline)

- v1 Jaccard paraphrase false-pass rate: **1.0**
- v1 heading-style wall false-fail: **True**
- v2 catch_rate: **1.0**

## Lock policy (honored)

减负 only if: n≥1000, quality ≥ baseline, catch_rate ≥ baseline, tokens ≤ 50%, **and live routing acc ≥ baseline**.
Live `SKILL.md` was **not** replaced.

`eval_skill.py` remains document lint. Final stdout: `SCORE 100.0  60/60  depth=standard source=routing.json`

Hashes: baseline `fnv1a32:14eeadf3` final `fnv1a32:14eeadf3`
