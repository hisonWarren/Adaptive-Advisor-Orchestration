# Prompts

Copy-paste blocks for switching between construction and critique, and for the single-model mitigation moves. Explicitly announcing a switch reduces unconscious engine drift and sycophancy; in a single-model run, fresh framing per phase also reduces stance carryover. Use order across the six phases: construction (Phase 2) → adversary and reality wall (Phase 3) → reconstruction (Phase 4, construction again) → second-order (Phase 6).

## Construction engine

> 现在切换到建设引擎。任务：为以下方向生成具体、可操作的方案细节。要求：(1) 只生成，不批判；(2) 细节可操作，不空泛；(3) 用领域内成熟方法学语言；(4) 若某点有疑问，标注"待审视"，但此阶段不展开质疑。生成覆盖不同轴的候选，而非同一方向的微调。

## Critique engine — adversary

> 现在切换到对抗者。严格按顺序：
> (0) 名单审查：这些角色是不是同一个先验戴了多顶帽子？指出一条它们都不会质疑的共同假设。找到则名单不合格。
> (1) Steelman：为当前方案构造最强版本，补全合理前提。此步不许批评。
> (2) Attack：攻击你刚构造的最强版本（不是草率原版）。必须是结构/前提/宏观适配问题，不接受"细节不完善"；至少一条让设计者无法用修补应对的批评。
> (3) Pre-mortem：设想两年后彻底失败，倒推 5–10 条深层原因。必含反馈回路探针："这个方案对系统做了什么，那个'什么'又如何反过来抵消它？"
> (4) 重构闸：每条存活批评给至少一条重构方向（哪怕"放弃，转向X"）。
> 红线：不接受"看起来合理"，只接受"在X条件下会被反假设否证"。单轮产出后交还，不进入天使/魔鬼死循环。

## Critique engine — reality wall

> 现在扮演那些不在场、却必须靠这个方案活下去的真人。逐一回答：他们要做这件事 N 次，每次时间/精力成本多少？方案默认的技能他们真有吗？情绪上扛得住、会真采纳吗？真实组织里会撞上什么非技术的墙？若涉及多个承受力冲突的真人，为每个人分别回答。另问一层证据陷阱："无人做过≠值得做——这个方向是真空白，还是数据稀缺/定义不一致/过早综合的伪空白？"最后判定：真人落得了地的方案，还是聪明但没人做得了的陷阱？

## Second-order meta-check

> 给出结论前，先做元层自检：(a) 我是否在不知不觉中只调用了某一套引擎？(b) 大家的赞同/反对更多来自语气还是论据？(c) 我们是不是太顺滑地一致了？(d) 有哪个我们都默认、却从没说出口的前提？显性回答这四个，再进入结论。

## Single-model mitigation

Because most runs are single-model, these turn the mitigation protocol into concrete moves. The first two are load-bearing.

**Externalize (cold review):**
> [In a fresh turn or context.] The following was written by someone else. Review it as an external auditor: run the adversary and reality wall against it. Do not assume it is correct because it reads well.

**Anchor to external evidence:**
> For each consequential claim below, check it against an external source (retrieval, data, or code execution) rather than asserting from memory. Tag anchored claims. For any claim with no external anchor, mark it "prior-only — unverified" and name which external check or which human would settle it.

**De-stance the problem (at Stage 0):**
> Rewrite this problem statement removing all stance and framing words (for example "promising", "obviously", "just"). State it as a neutral question, then proceed.

**Independent sampling (variance, not confirmation):**
> Regenerate this role or option in a separate pass without reference to the previous version. Note: if independent samples all agree, that is evidence of shared prior, not of correctness. Use disagreement across samples as signal; never treat agreement as confirmation.

**Name the human backstop (at close):**
> List every conclusion still marked "prior-only — unverified." For each, state the specific external check or the specific human who must settle it.

## Cross-model (only if the harness declares it)

> [Harness-level, not model-level.] Assign a different model family to the adversary and paradigm outsider than to the domain builders. The model cannot self-detect available families; whoever built the setup must declare them. Treat this as an opportunistic bonus layered on the single-model moves, never a precondition.
