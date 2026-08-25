# eval_lab — unattended stability loop

Quality score does **not** use `scripts/eval_skill.py` (that is document lint).

减负 (`reduce_skill`) will not touch live `SKILL.md` unless:

1. battery `n >= 1000`
2. `quality` ≥ baseline
3. `catch_rate` ≥ baseline
4. estimated tokens ≤ 50% of baseline

```bash
python3 eval_lab/gates/heterogeneity_check_v2.py --self-test
python3 eval_lab/gates/lint_output_v2.py --self-test
python3 eval_lab/battery.py
python3 eval_lab/loop.py
```

Reports: `eval_lab/reports/FINAL_REPORT.md`
State: `eval_lab/state/loop_state.json`
