# Execution Substrate

Roles are thinking structures; this file is about the machinery that runs them. SKILL.md carries the summary, the preflight, and the adaptive-entry decision tree — this is the depth. Read it when choosing how to run a panel, or when you need the single-model mitigation protocol in full.

## The three substrates

Capability-gated, but the *posture* is to use the most capable substrate the environment allows and the problem warrants — not to treat tools and agents as a rare opt-in.

| Substrate | What | When it is the right fit |
|---|---|---|
| **Sub-agents (orchestrator + context-isolated agents, one role per agent)** | The default for non-trivial problems when execution exists | ≥4 active voices, roles need independent context, parallel multi-source retrieval, or long-horizon/high-stakes work |
| **Tools inline (same model, tools by role and phase)** | Execution exists but the work is single-threaded | A few scripts and searches the facilitator runs inline, no parallel benefit |
| **Reasoning-only (one model, one context)** | Forced fallback when the preflight finds no code/web tools | No execution environment; must degrade loudly, never fake execution |

Reasoning-only is a *forced* state, not a preferred baseline. When it is forced, it is still fully runnable — but the run must announce it, downgrade confidence, and mark unverified claims. Capability-gating means the substrate scales to what exists and what the problem needs; the Stage 0 gate and the "do NOT open sub-agents" branch keep trivial problems from being over-machined.

## The hard rule: what sub-agents buy, and what they do not

Sub-agents and orchestration buy two real things:

- **Context isolation.** Separate contexts reduce cross-role anchoring and in-context stance drift — a genuine gain against the smooth-consensus failure mode. The gain grows with the number of agents.
- **Real tool execution.** Retrieval and compute actually happen instead of being imagined, which directly kills citation hallucination and evidence-from-memory.

They do **not** buy repair of shared prior. N sub-agents on the same base model are one prior in N hats; they cannot share weights across different models, and models converge toward near-identical outputs regardless of prompting strategy. The only things that break the shared-prior ceiling are cross-model generation (different weights) or a human.

Conflating these is the single biggest trap in upgrading. It produces a more expensive, slower, more authoritative-looking output that is exactly as homogeneous as one-model role-play — and looking more authoritative is the method's most dangerous state, because confidence that comes from the apparatus rather than from new evidence quietly suppresses the external checks that would catch the error.

A second, sharper warning: do not make the adversary a standalone agent that only objects, locked in angel-versus-devil counter-argument until a judge picks a side. That configuration performs worse than a plain single pass. Even when agent-ized, the adversary runs the full steelman → attack → reconstruction gate once and hands back.

## Single-model mitigation protocol

This protocol governs the REASONING-ONLY state, and it also runs as a backstop inside tool-enabled runs for whatever remains un-executed. It is what a single model can do about its own shared-prior and sycophancy ceiling. Note the scope carefully: it is a discipline for the *thinking*, not a reason to skip execution. When tools exist, run them — this protocol does not compete with tool use, it covers the residue. Cross-model is the strongest heterogeneity fix but does not happen automatically; it exists only when the harness exposes more than one model family, so "go cross-model" is, for most single-chat users, a dead pointer, and this protocol is the realistic substitute.

The governing fact: a model cannot reliably self-correct its own reasoning from its own feedback in the same context — attempts often fail and sometimes make things worse. But there is an exploitable asymmetry, the self-correction blind spot: a model fails to fix an error in its own output, yet fixes the identical error when it meets it as external input. The whole protocol flips the artifact from "my own output" into "foreign input."

**M1 — Externalize, then review cold.** Do not critique the plan in the same breath that produced it. Break the context: in a fresh turn or session, treat the artifact as something a stranger wrote, and only then run the adversary and wall on it. Same model, different context, and the blind spot lifts. This is why the six phases separate construction from critique; M1 makes that separation literal. In a single chat it is executable now — finish the draft, start a clean pass, treat the draft as third-party material.

**M2 — Anchor to external reality.** Intrinsic critique cannot break a shared prior; external evidence can, because retrieval, code execution, data, and falsification against observation are the one signal that does not come from the model's weights. For a single-model user, retrieval on the reality wall and the paradigm outsider is not a minor optimization — it is the primary substitute for cross-model heterogeneity. Every consequential claim the adversary or wall makes should, where possible, be checked against something external rather than asserted from the prior. A claim with no external anchor is marked "prior-only — unverified" and is never laundered into a finding.

**M3 — Do not seed the prior.** Sycophancy is largely front-loaded: a stance leaked in the framing ("here's my promising plan, evaluate it") shifts the answer more than any later rebuttal, and a long thread tends to increase sycophancy. So strip stance from the problem statement at Stage 0, prefer a neutral question to a loaded assertion, and prefer short independent passes to one long drifting conversation.

**M4 — Independent sampling, used correctly.** Regenerating a role or an option in a separate pass reduces intra-list conformity. But note the ceiling honestly: if samples share the prior they converge on the same answer, and majority voting masks the error rather than catching it; on capable models, extra samples can even degrade the result. Use independent sampling to surface variance, never to confirm. Agreement across same-model samples is evidence of shared prior, not of correctness.

**M5 — Name the human backstop.** After M1–M4 the residue is irreducible on one model. The Approver is not a rubber stamp here: for each claim still marked "prior-only — unverified," say which external check or which human would settle it. This is the honest terminus, not a disclaimer.

Ordering: M3 before you start → M1 and M2 during critique → M4 when generating alternatives → M5 at close. M1 and M2 are load-bearing; if you do nothing else, break the context and anchor to external evidence.

## Tool allocation by role and phase

Do not hand every role a retrieval tool. Blanket arming doubles token and latency cost and lets low-quality results pollute judgment.

| Role / phase | Default tool | Why |
|---|---|---|
| Reality wall | Retrieval | Check real constraints and the real failure rates of comparable cases |
| Paradigm outsider | Retrieval | Pull evidence from the adjacent field it speaks for |
| Domain builders (construction) | None by default | Pure reasoning; arming them front-loads noise |
| Facilitator | Evidence-integration ledger | De-dupe, source-tag, file evidence under issue numbers |
| Convergence step | Compute (RICE / weighted scoring) | On demand |

Every tool attachment needs a one-line reason — "why this step needs external evidence." No reason, no tool. See `retrieval-and-evidence.md` for the retrieval and integration detail.

## Facilitator KPI at high tier

If an orchestrator agent runs the meeting, its success criterion must include preserving and explicitly listing unresolved disagreement; treating "reached consensus" as success is forbidden. The better it organizes the meeting, the more it can smooth over real conflict — and smooth consensus is a danger signal, not an achievement. Efficiency serves decision quality; if it costs a real disagreement, it optimized the wrong thing.

## Cross-model, when it is present

If the running harness declares more than one model family, assign a different family to the adversary and outsider than to the builders — the single strongest lever against shared prior. The skill cannot auto-detect this; it cannot see its own harness, so any claim of "automatic cross-model detection" is false. Availability must be declared by whoever built the setup. Treat cross-model as an opportunistic bonus layered on top of M1–M5, never as a precondition the skill assumes.
