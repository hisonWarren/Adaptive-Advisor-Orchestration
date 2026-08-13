# Scripts

Four deterministic utilities (three run-gates plus one offline eval harness). Standard library only — no `pip install`. Each exits `0` on pass/success and `1` when it finds a blocking issue (`2` on bad input). Passing means the required structure holds, not that the reasoning is correct.

**Chaining the three on Windows.** Stock Windows PowerShell (5.1) does **not** support `&&`; only PowerShell 7+ and bash do. To stop on the first failure on 5.1, chain with a semicolon and an exit-code check rather than `&&`:

```powershell
python scripts\heterogeneity_check.py roster.json; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; `
python scripts\score_options.py options.json;     if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; `
python scripts\lint_output.py deliberation.md --interest-heavy; exit $LASTEXITCODE
```

On bash / PowerShell 7+, `cmd_a && cmd_b && cmd_c` works as expected.

## `heterogeneity_check.py`

Run at the end of Phase 1, before construction. Catches the collapses a model waves through: two roles sharing both red line and criteria, three roles that would veto for the same reason, a missing paradigm outsider, and a roster review that never named its shared assumption.

```
python scripts/heterogeneity_check.py roster.json [--threshold 0.6]
```

`roster.json`:
```json
{
  "roles": [
    {"name": "Quant methodologist",
     "red_line": "no uncorrected optional stopping",
     "criteria": "false positive rate controlled",
     "is_outsider": false,
     "veto_reason": "the error rate is not controlled"},
    {"name": "Clinical trial DSMB statistician",
     "red_line": "refuse the field's native jargon",
     "criteria": "pre-specified stopping rule and alpha spending",
     "is_outsider": true,
     "veto_reason": "there is no pre-specified stopping rule"}
  ],
  "roster_review": {
    "shared_assumption_named": "all roles assume publishing this result is the goal",
    "regenerated": false
  }
}
```

`--threshold` (default 0.6) is the token-overlap level at which two red lines or two criteria count as colliding. Token overlap is a cheap signal, not proof of genuine difference — a single model's roles still share a prior, so this catches obvious collapses but cannot certify real heterogeneity.

## `score_options.py`

Run in Phase 5. Deterministic weighted or RICE scoring, ranked. Removes transcription and weighting errors from scoring by hand. Output is input to the Approver, not a decision.

```
python scripts/score_options.py options.json
```

Weighted mode:
```json
{
  "mode": "weighted",
  "criteria": [
    {"name": "integrity", "weight": 0.30},
    {"name": "feasibility", "weight": 0.30}
  ],
  "options": [
    {"name": "Option A", "scores": {"integrity": 5, "feasibility": 2}},
    {"name": "Option B", "scores": {"integrity": 5, "feasibility": 4}}
  ]
}
```
Weights need not sum to 1; they are normalized. A missing cell is flagged, not silently zeroed.

RICE mode:
```json
{"mode": "rice", "options": [
  {"name": "Feature X", "reach": 8000, "impact": 2, "confidence": 0.8, "effort": 5}
]}
```
RICE = (reach × impact × confidence) / effort.

## `lint_output.py`

Run before finalizing. Enforces the output discipline the model tends to fake.

```
python scripts/lint_output.py deliberation.md [--interest-heavy]
```

Flags: phantom `[E-...]` citations (cited but never defined in an evidence-ledger row); conclusion lines (`结论:` / `Conclusion:`) with neither an `[E-...]` anchor nor a `prior-only — unverified` tag; a missing Verification Boundary or honesty/limitations section; and, with `--interest-heavy`, a reality wall showing fewer than two distinct per-person load tests. It checks scaffolding, not content — a clean lint does not mean the reasoning is sound.

## Design note

These scripts exist for the same reason the office skills ship `validate.py` and `accept_changes.py`: to make a discipline *actually run* instead of being asserted. They deliberately do **not** try to run the deliberation itself or call any model — reasoning is the model's job, and model orchestration is harness-dependent, not a portable skill utility.

Two robustness notes for real (esp. Windows) environments: input files are read with `utf-8-sig`, so a byte-order mark from PowerShell's `Set-Content -Encoding UTF8` is tolerated; and stdout is set to UTF-8 so non-ASCII (e.g. Chinese role names) prints correctly rather than as mojibake in a legacy-code-page console. `heterogeneity_check.py` also validates the roster shape and fails with an actionable message if `criteria` is a list or the review key is mis-named — a wrong schema stops loudly instead of silently running a weaker check.

**Do not reimplement these as inline `python -c` snippets.** The point is to run the tested files: the packaged checks are stronger than an obvious rewrite (token-overlap and veto-reason in the heterogeneity check; phantom-citation detection in the linter). An inline snippet that just prints an exit code satisfies the letter of the execution contract while defeating it.


## `eval_skill.py`

Offline mechanical eval of a skill directory. Scores routing licensed by `SKILL.md` + `routing.json` against `evals/evals.json`, then runs the three gate scripts on packaged fixtures. Author-path only -- do not open it on a user advisor run.

```
python scripts/eval_skill.py <skill_dir>
```

Exit 0 after printing `SCORE <n>  <passed>/<total>`. A score of 100 means the routing contract holds, not that a live panel produced a good decision.
