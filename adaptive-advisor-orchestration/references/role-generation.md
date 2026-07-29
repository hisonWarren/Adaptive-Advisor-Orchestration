# Role Generation

The procedure behind "let the problem grow its own review team," with the anti-pseudo-diversity checks built in. Roles are thinking structures, not credentials — high-risk domains still need real experts.

## Axis selection (before generating any role)

Answer three questions:

1. Would two domain experts with different specialties likely agree on direction? If yes, domain alone is insufficient — the fight is not about knowledge; add an interest axis or an outsider. If no, the domain axis is live.
2. Are there absent people whose tolerance for the outcome differs from each other? If yes, the problem is interest-heavy and the reality wall runs per person.
3. Is the hidden fight about what is true, or about who bears the cost? Truth → domain. Cost or burden → interest. Both → cross the axes.

| Result | Decompose by | One role per |
|---|---|---|
| Domain-heavy | MECE knowledge domains | independent domain |
| Interest-heavy | conflicting stakeholders | who is affected / decides / executes / pays |
| Both | cross the two, then compress to ≤7 | — |

Interest decomposition resists pseudo-diversity better: stakeholders conflict for structurally different reasons, which is harder to fake than five domain experts sharing one prior. Use domain decomposition when the fight is genuinely about what is true.

## Role card

```yaml
角色:        # a real-identity title — expert type, user type, or stakeholder. NOT "expert"/"advisor"
视角原型:    # who in reality this maps to
关注点:      # 2–4 things it cares about most
提问范式:    # 2–3 questions it repeatedly asks
红线:        # non-negotiables — MUST differ from every other role
评价标准:    # how it judges good vs bad — MUST differ from every other role
何时禁用:    # when this role slows or misleads; when to retire it
挂工具:      # retrieval? (default only for reality wall + outsider) — with a one-line reason
```

No vague roles. Every role is a concrete real-world identity — a specific profession, user type, or interested party — derived from an axis dimension. Red lines and evaluation criteria must differ across roles; two roles sharing both are one role, so merge them.

## Mandatory guards and outsider (always add)

```yaml
# Adversary (calibrated red team) — every time
角色: 对抗者
工作流: 名单审查 → Steelman → Attack（攻最强版，一条无法修补的批评）→ Pre-mortem（含反馈回路探针）→ 每条批评给一条重构方向
红线: 不接受"看起来合理"；只接受"在X条件下会被反假设否证"

# Reality load-bearing wall — every time; per-person on interest-heavy problems
角色: 现实承重墙
视角原型: 缺席的、必须靠这个方案活下去的真人（利益重：每个受影响真人各跑一次）
关注: 时间精力 / 技能认知 / 情绪意愿 / 组织约束 + 证据陷阱（"无人做过≠值得做"）
现实闸门: 聪明但真人扛不住/不会用 = 陷阱，降级或放弃

# Paradigm outsider — every time, at least one
角色: 范式局外人
视角原型: 来自完全不同领域、不接受本问题母语术语的人
任务: 用陌生领域语言重述问题；指出本领域默认却从未被质疑的前提
红线: 拒绝用问题母语术语作为答案主导词汇

# Second-order observer — checklist by default; a role only if the panel exceeds seven
```

The human is the Approver (DACI) and is never simulated.

## Heterogeneity check (after generation, before construction)

Run all, in a separate pass from generation:

1. **Red-line / criteria pairwise check.** Any two roles sharing both red line and criteria → merge.
2. **Veto-reason test.** Imagine each role vetoing the same draft. Same reason three times → pseudo-diversity, regenerate.
3. **Adversary roster review.** Name one assumption no role would challenge. Found → roster fails. State the shared assumption explicitly; if regenerating, state what changed. Never mark "pass" without naming the checked assumption.
4. **Paradigm outsider present.** At least one role rejecting native terminology.
5. **Cross-model if the harness declares it** (strongest lever); otherwise this is a single-model panel — apply the single-model protocol, and remember that same-model agreement is not evidence of correctness, only of shared prior.

## Machine-checkable roster

To run `scripts/heterogeneity_check.py`, express the roster as JSON: a `roles` array where each role has `name`, `red_line`, `criteria`, `is_outsider` (boolean), and `veto_reason` (why it would veto the current draft), plus a `roster_review` object with `shared_assumption_named` (the one assumption no role would challenge, or null) and `regenerated`. The script flags any pair sharing both red line and criteria, three or more roles sharing a veto reason, a missing outsider, and an unnamed shared assumption. Full schema and exit codes are in `scripts/README.md`. Passing is a floor, not a ceiling — token overlap cannot certify that a single model's roles are genuinely heterogeneous.

## Failure modes

Vague roles ("expert / advisor / stakeholder") — use a concrete identity from an axis. A fixed roster reused across problems — regenerate per problem. Pseudo-diversity (different labels, same prior — all engineers who love the same architecture) — catch it with the veto-reason test, roster review, and outsider. An empty heterogeneity "pass" that never names the shared assumption. Too many roles for a small problem — minimize; add a role only when it brings a red line no other role has.
