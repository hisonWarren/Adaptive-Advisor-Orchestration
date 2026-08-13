---
name: adaptive-advisor-orchestration
description: "Use this skill for any question or request whose best answer needs more than one perspective and a real evidence trail: architecture and RFC choices, methodology and research design, policy or organizational trade-offs, high-risk changes (data, migration, security, compliance), strategy, comparisons, family or interpersonal decisions with conflicting stakes, or anything a user asks expecting a thorough, well-grounded answer — even when they do not name a method or add any trigger word. Trigger whenever a problem has real disagreement inside it (competing domains, conflicting interests, or a seductive answer that hides a trade-off). It assembles a problem-specific review panel with a permanent adversary, a reality wall for absent affected people, and a paradigm outsider, and runs a six-phase construction-critique-reconstruction workflow. By default it runs EXECUTE (scripts and searches actually run); depth defaults to Standard: it detects whether code/web tools are available and, if so, actually runs its scripts and searches and shows the command+exit-code evidence, entering sub-agents adaptively for non-trivial problems; if no tools exist it says so and downgrades confidence rather than faking execution. Do NOT use it for simple lookups, trivial one-step edits, settled questions with a clear best practice, or emergencies needing immediate action — it self-rejects on those."
license: Proprietary. LICENSE.txt has complete terms
---

# Adaptive Advisor Orchestration

Version: **0.3.1** (gated speaker card)

Let the problem grow its own review team — but always anchor three roles that do not depend on the problem: an adversary that attacks the hard core, a reality wall that represents the real people who must live with the decision, and at least one outsider who does not speak the problem's native language. The output is auditable, decision-oriented, and honest about its own limits — not role-play chatter.

Four commitments hold no matter what the problem is:

1. Multi-perspective critique beats single-perspective self-review — **only when the perspectives are genuinely heterogeneous.** Lose that and multiple roles collapse into mutual agreement, worse than one honest voice.
2. The adversary is structurally present, never decorative or optional.
3. Final authority stays with the human (the Approver).
4. Roles are thinking structures, not credentials. High-risk domains still need real expert sign-off.

## Quick execution checklist

The executing agent is the **facilitator**: it runs the phases in order, enforces the gates, and never skips a guard to save effort.

```
[ ] Preflight FIRST: declare EXECUTE / EXECUTE+NET / REASONING-ONLY (bare invocation = Standard depth + EXECUTE scripts; no flag needed)
[ ] Substrate: enter sub-agents by default on non-trivial problems (≥4 voices, parallel retrieval, high stakes); do NOT for trivial/settled ones
[ ] Phase 0: ≤300-word problem + two-question gate + speaker card or `situated: unspecified` → proceed or reject
[ ] Phase 1: axis selection → roles + cards → guards + outsider → heterogeneity check (incl. roster review)
[ ] Phase 2: 2–4 candidate options; guards mostly silent; axis-coverage check
[ ] Phase 3: adversary steelman→attack→pre-mortem; wall load-test per affected person; critique only
[ ] Phase 4: reconstruct every surviving criticism; wall re-check; drop traps
[ ] Phase 5: numeric prioritization + consensus map + Approver decision slot
[ ] Phase 6: second-order checklist + stop signal
[ ] EXECUTE state: run required scripts, use tools where phases call for them, show command + exit code; anchor load-bearing claims to real output
[ ] EXECUTE+NET: reality wall and outsider ground claims in real searches, not priors
[ ] REASONING-ONLY: label it, downgrade confidence, list prior-only-unverified claims — never look executed when nothing ran
[ ] Fail-closed verdict LAST: missing script log/exit code, or unanchored claim with no prior-only tag ⇒ INVALID, repair and rerun
[ ] Always include: verification boundary + honesty notes
```

**Output depth.** Default to **Standard**. Use **Full** when stakes are high or the user wants the full audit trail; use **Minimal** under time pressure (guards still mandatory). Each role speaks in stance + red line + one concrete recommendation, not monologues. The adversary must produce at least one attack that cannot be patched and one reconstruction direction. The wall must name specific people and specific failure modes, not "users may resist."

**Routing ceilings (machine-checkable in `routing.json`).** EXECUTE means scripts actually run, not Full depth. Bare invocation = Standard depth + EXECUTE. Full is opt-in.

| Class | max_agents | max_refs | scripts | when |
|---|---|---|---|---|
| Minimal | 0 | 0 | none required | `relaxed: prioritize speed` or Stage 0 gray + time pressure |
| Standard | 4 | 1 | heterogeneity_check + lint_output | default |
| Full | 8 | 3 | all three | high stakes or user asks Full |

Open `references/role-generation.md` only if Phase 1 axis selection is non-obvious. Open `references/facilitation.md` only if panel size >= 4. Open `references/retrieval-and-evidence.md` only in EXECUTE+NET when a load-bearing claim needs a ledger row. Do not always-read the six reference files.

**Sibling handoff (refuse-and-route).** If the problem is a domain pipeline that already has a skill (dockerHDDM/HDDM inference, paper-writing pipeline), Stage 0 refuse-and-route: do not emit that domain's sample code here and do not absorb its notebooks into this skill. See `references/skill-handoff.md` (read-when: Stage 0 detects a sibling).

**Generated tools and supervision.** A same-model supervisor agent is forbidden. Generated helpers are Full-only, disposable, one per run, only if the three packaged scripts cannot cover the check, and must be deleted after the run; default OFF. Do not write generated scripts into the skill tree on a user-path run.

**Closed menu; no mid-run Adapt.** The facilitator may select NGT / Delphi / 1v1 / Hats from the existing facilitation menu. It may not invent a new 12-phase process or open an Adapt-Explore loop mid-run. Institutional learning (revisiting the skill itself) is between runs, via `evals/` and the human Approver.

**Evals (author path, never always-read on a user run).** `evals/evals.json` plus `python scripts/eval_skill.py <skill_dir>`. Failures that stay red after a patch block promotion.


## Execution contract (default, no trigger word needed)

This is the heart of the skill and it runs **by default on a bare invocation** — the user does not type "strict" or any flag. EXECUTE (scripts and searches actually run; no fake execution) is the default posture. Output *depth* defaults to Standard. Full depth is opt-in (high stakes or the user asks). The only thing a flag can do is *relax* depth to Minimal. The reason this section exists: prose that merely *says* "run scripts" gets rationalized away by the model's deepest default — "text is done, so I'm done." This contract is written as **actions the model performs**, opened by a preflight and closed by a fail-closed verdict, so execution cannot be silently skipped.

### Execution preflight (do this first, before Phase 0)

At the very start, detect the actual runtime capability and **declare one of three states in one line**. This declaration is mandatory and appears in the output.

- **EXECUTE** — code execution is available (a bash/python tool). Then scripts **must** run, tools **must** be used where the phase calls for them, and every consequential claim is anchored to real output. Skipping available execution is not allowed.
- **EXECUTE+NET** — code execution *and* web retrieval are available. As above, plus the reality wall and paradigm outsider **must** ground their load-bearing claims in real searches, not priors.
- **REASONING-ONLY** — no code/web tools exist in this environment (e.g. a plain chat surface). Then the skill runs the full reasoning workflow but **must say so loudly**: label the run REASONING-ONLY, downgrade stated confidence, and list which conclusions are therefore `prior-only — unverified` and what execution or human check would settle them. It must **never** produce text that looks executed when nothing ran.

The disease was never "no tools ran." It is "nothing ran *and the output didn't say so*." The preflight makes the state explicit and binds behavior to it.

### Fail-closed verdict (do this last, before finalizing)

Before the final answer, check the contract. In **EXECUTE / EXECUTE+NET** state, if any required script has no command + exit code shown, if the "script log" is an inline reimplementation rather than a call to the packaged `scripts/` files, or if any load-bearing claim is unanchored with no `prior-only` tag, the response is marked **INVALID — execution incomplete**, and the model repairs and reruns rather than shipping it. In **REASONING-ONLY** state, "valid" requires the explicit REASONING-ONLY label, the confidence downgrade, and the unverified-claims list — a reasoning-only run that hides its own limits is equally INVALID. Fail-closed is conditional on capability: it blocks *pretending*, not *thinking*.

### Relaxing the default (explicit opt-out only)

The default needs no flag. To make a run lighter, the user must say so explicitly, e.g. `relaxed: prioritize speed`. In relaxed runs the skill still declares its preflight state and still lists, plainly, every check it skipped and the residual risk. Ambiguous or bare messages always take Standard depth + EXECUTE, never the relaxed path.

## When to apply

Apply when the request involves one or more of: complex trade-offs (speed vs quality, UX vs compliance, innovation vs stability); architecture, RFC, methodology, or planning decisions with no obvious best practice; policy, organizational, interpersonal, or family decisions with conflicting stakeholder interests; unclear scope with several valid paths; high-risk changes to data, migration, security, reliability, or compliance; or an explicit ask for a panel, red team, pre-mortem, or decision workshop.

Do not apply to trivial one-step edits unless the user explicitly asks.

## Stage 0 · Problem qualification

Run this **before** assembling any panel.

**Write the problem in ≤300 words.** Isolate the question, expose vagueness, and separate facts from assumptions. This step alone surfaces a lot.

**Two-question rejection gate.** Ask both: (1) Does a recognized best practice already exist? (2) Are risk and uncertainty both low? If **both are yes**, do not convene a panel — execute the best practice directly. This is the clear/simple case, and over-deliberating it is waste.

**Chaos check.** Crisis, outage, emergency, or a closing decision window → do not convene. Act first to restore basic order; evaluate afterward. Running six phases during an emergency misses the window.

**Applicable contexts.** The method fits **complicated** problems (a causal structure exists and can be reasoned through) and **complex/emergent** ones (no single best practice; outcomes depend on feedback and context). Most "who should we involve?" questions live here.

**Gray zone.** When an unusual factor — a novel constraint, an odd compliance requirement — introduces uncertainty with no ready best practice, the problem slides from clear to complicated and the method may trigger. Use the Minimal Version when time is tight.

**Speaker card (gated).** If the run proceeds and the deliverable will be first-person or published under a named person, write one line before the panel: who is speaking, in what register, and which situation examples must come from. Use only what the problem, byline, or workspace already states. Do not invent a biography. If the deliverable is not first-person/public, write `situated: unspecified` and continue — do not tax an RFC or other non-authored task with a life story. Accessibility rewrites terminology; it does not recast a situated speaker into an unrelated stock persona.

## Role system

Three layers, always composed together:

| Layer | What | Rule |
|---|---|---|
| **Adaptive roles** | Problem-specific perspectives | Generated per problem; keep the count minimal |
| **Permanent guards** | Adversary + reality wall (+ second-order check) | Non-negotiable every time |
| **Paradigm outsider** | At least one role that rejects the problem's native terminology | Mandatory every time |

The paradigm outsider rejects native terminology, not the speaker's life. A stock persona swapped in to sound accessible is a failed outsider, not a successful one.

The human user is the **Approver** (DACI). Never simulate the Approver.

Full generation procedure — axis selection, role cards, and the heterogeneity check — is in `references/role-generation.md`. The essentials:

**Axis selection (do this before generating roles).** Ask where the real disagreement lives. If two domain experts with different specialties would still agree on direction, domain alone is insufficient — add an interest axis or an outsider. If there are absent people whose tolerances conflict, the problem is interest-heavy and the wall runs per person. If the hidden fight is about what is true, decompose by **domain** (one role per independent knowledge area); if it is about who bears the cost, decompose by **interest** (who is affected / decides / executes / pays); if both, cross the axes and compress to ≤7 voices. Interest decomposition resists pseudo-diversity better, because stakeholders conflict for structurally different reasons that are harder to fake than five domain experts sharing one prior.

**Panel size sets the method.** ≤3 → 1v1 or tight round-robin. 4–7 → Nominal Group Technique (independent generation → share → vote). 8–12 → Delphi (two anonymous rounds) or Six Thinking Hats. >12 → subgroup (≤5 each) with structured inter-group docs. Prefer 4–8 active voices including guards and outsider. Run-scripts for each method are in `references/facilitation.md`.

**Every role fills a card** with a real-world identity (never "expert" or "stakeholder"), its concerns, the questions it repeatedly asks, its red line, and its evaluation criteria. **Red lines and evaluation criteria must differ across roles** — that is where heterogeneity is enforced. Two roles sharing both are one role; merge them.

## Permanent guards

These do not scale with problem size. They guard against method failure, not problem content.

### Adversary (calibrated red team)

Guards against framework lock-in, patching the guardrails instead of the core assumption, and sycophancy. It works in this order:

0. **Roster review, before construction.** Attack the panel itself: "Are these roles one prior in different hats? Name one assumption none of them would challenge." If found, the roster fails — regenerate.
1. **Steelman.** Build the strongest version of the current option, filling in unstated but valid premises. No criticism in this step.
2. **Attack.** Attack the steelmanned version, not a strawman. The attack must be structural, about premises, or about macro-fit — not "needs more detail" — and must include at least one criticism the designer cannot fix by patching alone.
3. **Pre-mortem.** Imagine total, public failure about two years out; derive 5–10 deep causes, favoring "we should have seen it coming." Include one **feedback-loop probe** on emergent, interest-heavy, or org/policy problems: "What does this plan do to the system, and how does that feed back to cancel the plan?" On purely technical problems where feedback is unnatural, substitute a **falsification probe**: "Under what observable condition would this be clearly wrong, and would we detect it before sunk cost?"
4. **Reconstruction gate.** For each surviving criticism, give at least one reconstruction direction — even "abandon, pivot to X."

The adversary's red line: it does not accept "seems reasonable." It accepts only claims falsifiable under stated conditions. Pure opposition is forbidden because it causes critical paralysis — twenty problems, no priorities, silence when asked what to do. Calibrated adversarial work is fierce but always lands a reconstruction. Run it **once** and hand back; never loop into angel-versus-devil counter-argument.

### Reality load-bearing wall

Guards against clever plans that real humans cannot execute or accept. It represents the absent people who must live with the decision, across four question classes: **time and energy** (how often must a real person do this, and what is one extra second of friction times N repetitions?); **skill and cognition** (does the plan assume abilities the target person has, and how steep is the curve?); **emotion and willingness** (can they bear the change, or will they quietly work around it?); and **organization and constraints** (what non-technical walls — incentives, politics, inertia, regulation — will it hit?).

Also run a quick **evidence-trap check**: "nobody has done this" is not "worth doing." Is the gap real, or caused by data scarcity, inconsistent definitions, collinear parameters, or premature synthesis? A direction empty because it is a data trap fails the same way a human-rejecting plan does.

On interest-heavy problems the wall is **not one voice**. Run the load test **once per affected person** — parent, spouse, the burned-out future self — because their tolerances conflict, and collapsing them into one "user" flattens the real conflict.

Reality gate (hard): before convergence, every surviving option must pass the wall. A clever plan real humans will not use is a **trap**, not "needs improvement" — downgrade or abandon. Its red line: a theoretically perfect but operationally exhausting or human-rejecting plan loses to an operationally smooth, human-accepting, theoretically-fine one.

### Second-order observer

Guards against groupthink, mutual reinforcement, and dominance by the loudest voice. By default the facilitator runs a checklist at the end of each phase; it becomes an independent role only when the panel exceeds seven. The checklist: Did we lock into a frame too early? Did we agree too smoothly? Is anyone repeating others without new reasoning? Whose stance comes from tone rather than evidence? What unstated premise did we all assume?

## Heterogeneity protocol

The deepest risk of any multi-role method is pseudo-diversity: different labels, same prior. Run this after role generation and before construction.

1. **Red-line / criteria pairwise check.** For any two roles, do red lines differ? Do evaluation criteria differ? If both match, merge.
2. **Veto-reason test.** Imagine each role voting against the same draft. Would the reasons differ? Three identical veto reasons means pseudo-diversity — regenerate.
3. **Independent sampling.** Generate roles in separate passes when possible, not one shot; one-shot listing lets later roles accommodate earlier ones.
4. **Adversary roster review.** Find one assumption no role would challenge. If found, the roster fails. **Name the shared assumption explicitly**; if regenerating, state what changed. Never mark "pass" without naming the assumption checked — an empty pass is theater.
5. **Paradigm outsider present.** At least one role that rejects the native terminology, not the speaker's life.
6. **Smooth-consensus watch.** Fast unanimous agreement is a danger signal; introduce sharper opposition or a human checkpoint.

Multi-agent debate only beats repeated single-agent sampling when genuine perspective differences exist; heterogeneity must be constructed and verified, not assumed. On a single model instance, all roles — adversary, wall, and outsider included — share weights and the same sycophancy bias, and a model cannot reliably self-correct its own reasoning from its own feedback. Structural gates reduce this but cannot remove it. The realistic mitigations are the single-model protocol in `references/execution-substrate.md` (review the artifact cold as external input, anchor claims to external evidence, keep prompts stance-free, use independent sampling to surface variance rather than to confirm) plus a named human backstop. Cross-model generation helps most but is an opportunistic bonus, not an assumption. **Same-model agreement is never evidence of correctness — only of shared prior.**

## Execution substrate

Roles are thinking structures; this is about how they run. The posture is: **when the environment offers execution and the problem is non-trivial, use it — tools and sub-agents by default, entered adaptively.** Agents are not an optional upgrade reserved for special cases; they are the default vehicle for the two things they genuinely buy, withheld only when the problem is clearly too small to warrant them. Full detail, including the single-model mitigation protocol and tool-by-role allocation, is in `references/execution-substrate.md`.

**What sub-agents buy — used aggressively — and the one thing they do not.** Sub-agents and orchestration buy **context isolation** (separate contexts cut cross-role anchoring and stance drift — a real gain against smooth consensus, growing with agent count) and **real tool execution and parallelism** (retrieval and compute actually happen, in parallel, instead of being imagined — this kills citation hallucination and compresses wall-clock time). These are reason enough to use them by default on any non-trivial run. The one thing they do **not** buy is repair of shared prior: N sub-agents on the same base model are one prior in N hats, and only cross-model generation (different weights) or a human breaks that ceiling. So: **use agents freely for isolation, real execution, and parallelism; do not mistake them for diversity.** That caveat narrows what you *claim* from agents — it does not push you back to a single context.

### Adaptive entry — the decision tree

Enter the substrate that fits the problem, reassessed at Phase 0:

- **Sub-agents (default for non-trivial problems), when any hold:** the panel has ≥4 active voices; roles need independent context to avoid anchoring; retrieval or evidence integration spans multiple sources that can run in parallel; the run is long-horizon or high-stakes. Dispatch one role per context-isolated agent; route tools by role and phase; the orchestrator must return preserved open disagreements, never a smoothed consensus.
- **Tools without sub-agents, when:** execution is available but the problem is single-threaded — a few scripts and searches the facilitator runs inline, no parallel benefit.
- **Do NOT open sub-agents (hard branch), when:** the Phase 0 two-question gate would reject the panel; ≤3 perspectives cover it and the root cause is known; the answer is a single lookup or a settled best practice. Spinning up agents for a trivial question is the failure the "no absent humans" rule warns about — the correct execution amount for a simple question can be zero agents and zero scripts. Adaptive means the machinery scales to the problem, not that maximum machinery runs every time.

In **REASONING-ONLY** state (preflight found no tools), none of the above can run; apply the single-model mitigation protocol below and keep the loud degradation the preflight requires.

### Single-model mitigation protocol (for REASONING-ONLY, and as backstop)

When execution is genuinely unavailable, the run still has two load-bearing moves. **Review the artifact cold** — in a fresh pass, treat the draft as something a stranger wrote before running the adversary and wall on it (a model fixes an error it meets as external input that it cannot fix in its own output). **Anchor to external evidence wherever any exists** — and where none does, mark the claim `prior-only — unverified`, never laundered into a finding. Same-model agreement is never evidence of correctness, only of shared prior.

## Six-phase workflow

The rhythm is heavy construction → heavy critique → reconstruction. Let options form before attacking, then land them in reality. Copy-paste engine-switch prompts for each phase are in `references/prompts.md`.

**Phase 0 · Qualification.** Run Stage 0. Output: problem statement + speaker card or `situated: unspecified` + applicability verdict.

**Phase 1 · Role generation.** Axis selection → decompose → fill role cards. Add the two hard guards plus at least one paradigm outsider. Decide second-order as checklist or role (role only if >7). Run the full heterogeneity protocol including the adversary roster review. Apply panel-size rules. Output: roster + completed cards.

**Phase 2 · Construction.** Domain and stakeholder roles propose and build options boldly, no pre-critique. Adversary (after roster review) and wall stay mostly silent — keep the suits out. End with an axis-coverage check: do candidates cover different angles, or micro-tune one? Output: candidate options.

**Phase 3 · Adversarial round.** Adversary: steelman → attack the core → pre-mortem with the feedback-loop probe. Wall: four question classes plus the reality gate, per affected person on interest-heavy problems. Critique only — no patching this round; target core assumptions, not polish. Output: core criticisms + reality-gate results.

**Phase 4 · Reconstruction.** For each surviving criticism, reconstruct or consciously accept it as a constraint. Pointing out problems without a reconstruction path is forbidden. The wall re-checks reconstructed options: can real humans do this now, within tolerance? Options failing the reality gate are downgraded or dropped. Output: reconstructed viable options.

**Phase 5 · Convergence and accountability.** Numeric prioritization (RICE / weighted multi-criteria / Multi-Voting / MoSCoW). Explicitly separate full consensus, partial consensus (who aligns with whom), and genuine unresolved disagreement. Do not force-merge genuine disagreement — log it as an open item. The human Approver decides under DACI. Output: ranked options + decision record.

**Phase 6 · Second-order review and stop.** Run the second-order checklist. Stop when marginal benefit drops below cost — if direction is stable, key risks are identified, and further rounds would add noise, stop.

## Convergence tools

| Tool | When | Output |
|---|---|---|
| **RICE** | Many candidates; prevent halo effect | Numeric rank |
| **Multi-Voting** | Many candidates; quick narrowing | Vote distribution |
| **MoSCoW** | Scope cutting; prevent over-build | Must / Should / Could / Won't |
| **Weighted multi-criteria** | Balance across innovation, feasibility, value, falsifiability, human tolerance | Per-dimension 1–5 + composite |
| **DACI** | Accountability | Driver / Approver / Contributors / Informed (human = Approver) |

## Minimal version

Use when time is tight but the problem is not clear/simple or chaotic. Phase 0 becomes a one-sentence qualification plus the two-question gate plus speaker card or `situated: unspecified`. Phase 1 becomes 2–3 adaptive roles plus the two hard guards plus one outsider. Phases 2–4 become one round per role, where the adversary must still run roster review, steelman, and one attack, and the wall must pass the reality gate. Phase 5 becomes a three-dimension sort (innovation, feasibility, human tolerance). Phase 6 becomes a one-sentence second-order check. **The adversary, reality wall, and paradigm outsider are never optional, even here.** A rough output with all three guards present beats a polished output where domain roles only agree with each other.

## When not to use

- **Clear context** — passes the two-question gate; execute the best practice.
- **Chaos context** — crisis needing immediate action; act first.
- **Small problem** — ≤3 perspectives cover it and the root cause is known; 1v1 suffices.
- **Diminishing returns** — options stable, risks identified, key people aligned; stop, don't add rounds for the appearance of thoroughness.
- **No absent humans and no hidden dilemma** — the method's marginal value over a plain competent answer is roughly the number of absent affected people plus the number of dilemmas the obvious answer hides. On a purely technical problem with no absent stakeholders and no buried trade-off — an isolated algorithm or library choice — a capable model already reaches the hard core unaided and the reality wall runs empty. The panel adds structure but little substance; prefer the Minimal Version or a plain answer.
- **Low psychological safety** — for real teams, build safety before heavy critique, and critique the plan, not the person.

**Psychological safety mode.** When the problem involves real named colleagues, recent conflict, performance blame, or retaliation risk: the adversary attacks options and incentives, not individuals' competence or character; prefer a private facilitator summary to the Approver over quotable "role X said you failed"; add a rule that no motives are attributed to real people, only structural incentives; the wall names roles and situations, not "Bob is lazy." If the ask is pure interpersonal adjudication ("who is wrong, A or B?") with no decidable plan, reject the panel and route to mediation.

## High-stakes expert review

For legal, regulatory, clinical, financial, export-control, or cross-border-data problems: always populate a **needs human expert review** slot with the named domain ("EU GDPR counsel", "China PIPL local counsel"), never a generic "consult a lawyer." Simulated roles must not state compliance conclusions as fact — use "reasoning suggests X; blocker until licensed review confirms." If a compliance conflict is unresolved after Phase 4, the decision slot stays open; do not fabricate closure. The paradigm outsider widens framing but cannot substitute for licensed review.

## Output format

Organize every phase's output as numbered issues and sub-points, not loose sections. This costs almost nothing but forces three things that otherwise get skipped: running the wall per person, landing every sub-point on a concrete conclusion, and explicitly listing open items. An issue is `Tn` (one independent question); a sub-point is `Tn.m` (each separately answerable); every `Tn.m` ends in a one-line conclusion; evidence is anchored as `[E-Tn.m-k]`, one-to-one with the conclusion it supports. Discuss sub-point by sub-point; do not skip or merge; close all sub-points of an issue before the next.

Within that skeleton, produce:

- **Problem qualification** — statement (≤300 words), speaker card or `situated: unspecified`, context type (clear / chaos / complicated / emergent), gate result.
- **Panel setup** — axis choice, adaptive roles, permanent guards, paradigm outsider, panel method, heterogeneity result (pass or regenerated, and why).
- **Construction** — candidate options.
- **Adversarial findings** — roster review; steelman summary; core unpatchable attacks; pre-mortem plus feedback-loop probe; wall load-tests per person; reality gate per option.
- **Reconstruction** — changes per criticism; post-reconstruction reality check.
- **Convergence** — prioritization method and scores; full consensus; partial consensus; genuine open disagreements.
- **Decision (ADR-style)** — context; decision; consequences; deferred items with triggers; irreplaceable human actions (conversations, consent, licensed sign-off — not simulable).
- **Second-order review** — process-health check; stop rationale.
- **Verification boundary** — verified now by reasoning; needs human expert review; needs runtime or user validation.
- **Honesty notes** — method limits affecting this decision; the single-model caveat where it applies.

## Minimum delivery checklist (must appear in final response)

Before marking complete, ensure the final response includes all items below:

1. **Preflight state**: `EXECUTE` / `EXECUTE+NET` / `REASONING-ONLY`, plus (if relaxed) the explicit relaxed note.
2. **Substrate used**: sub-agents / tools-inline / reasoning-only, and one line on why that fit the problem's size.
3. **Script run log** for required scripts in EXECUTE states (or, in REASONING-ONLY, a plain statement that no execution was possible):
   - command
   - input file(s)
   - output summary
   - exit code
4. **Evidence grounding**: which references were read and where they influenced the decision; in EXECUTE+NET, the real searches behind load-bearing claims.
5. **Gate status**: pass/fail at each mandatory gate; rerun notes if any gate initially failed.
6. **Fail-closed verdict**: an explicit statement that the contract passed — or the INVALID marker with what is being repaired.
7. **Verification boundary and honesty notes** (cannot be omitted).

## Stop rules

Stop iterating when any of these holds: the latest round yields only wording changes with no structural shift; improvements conflict (fixing A breaks B) at a Pareto frontier; key design choices have stabilized and the rest is taste; the deepest limit (the single-model heterogeneity ceiling) is confirmed irreducible — mitigate externally, don't pretend it is solved; or the Phase 6 marginal-benefit check says further rounds add noise. Announce the stop explicitly and list what remains open.

## Honesty discipline

1. Roles are thinking structures, not human experts. High-risk domains — clinical, legal, financial — require real expert review.
2. Single-model residual bias is irreducible by structure alone, and sub-agents do not fix it. Same-model sub-agents give context isolation and real tool execution but share the prior, and the model cannot reliably self-correct from its own feedback. Since cross-model is rarely available automatically, the working mitigation is the single-model protocol: review the artifact as external input, anchor consequential claims to external evidence, keep prompts stance-free, use independent sampling to surface variance rather than confirm, and name the human backstop for what stays unverified. Reach for agent orchestration to get real tool execution and context isolation, not to manufacture diversity.
3. Do not claim "validated" or "optimal." The output is multi-perspective reasoning, not proven reality. On "optimal," target the attainable frontier — each retained choice should survive real alternatives, residual limits are labeled, and you stop when marginal improvement costs more than it returns.
4. The human Approver owns the final judgment, always.
5. The method can become its own lock-in. Periodically ask where it was run mechanically and which decisions should have skipped it. The Stage 0 gate exists for this.
6. Checklist theater is worse than a single honest perspective. Each phase output must be concrete and externally auditable. If the adversary's criticism does not discomfort the designer, it is not working.
7. Pseudo-diversity cannot be fully tested — surface-different red lines may still share a deep prior. Mitigate as in point 2.

## Hard constraints

Never frame simulated roles as real credentialed sign-off. Keep human decision authority explicit. The adversary, reality wall, and paradigm outsider are never optional. Prefer failing loudly to failing silently. Report unresolved safety or compliance risk as a blocker, not a soft note. Keep the rationale traceable end to end. Critique without a reconstruction path leads to critical paralysis and is forbidden.

## Anti-patterns

Too many roles for a simple task. A fixed roster reused for every problem. Making the guards adaptive so the model can omit or soften the adversary. Merging the adversary and reality wall, which attack different failure modes. Role chatter with no decision impact. Treating smooth unanimous agreement as success. Compromise with no owner (missing DACI). No explicit decision criteria or numeric prioritization. No deferred trigger on open items. Running the full six phases on clear or chaotic problems. Endless rounds chasing "optimality" past diminishing returns. Marking heterogeneity "pass" without stating the shared assumption checked. Simulated compliance sign-off without an expert-review slot on regulated topics. The adversary attacking a real named colleague's character in a team-conflict setting. Making the adversary a standalone "only-objects" agent in an endless angel-versus-devil loop — it runs steelman → attack → reconstruction once and hands back. Using same-model multi-agent to fake heterogeneity — it is one prior in N hats; for real heterogeneity go cross-model or human. Reproducing the packaged scripts as inline `python -c` snippets to manufacture an exit code while skipping the stronger real check — call the files in `scripts/`, or declare REASONING-ONLY. Recasting a situated speaker into a stock persona to sound accessible. Inventing a biography on a task that is not first-person or public.

## Scripts

Three deterministic utilities remove error sources the model otherwise fakes by free-form reasoning. They use only the Python standard library (no install). In **EXECUTE / EXECUTE+NET** state these run at the points below with command + output summary + exit code shown (the fail-closed verdict enforces it); in **REASONING-ONLY** state they cannot run, so their checks are performed by hand and explicitly flagged as unverified. Passing means the *structure* holds, not that the reasoning is sound.

**Call the packaged scripts — do not re-implement them inline.** The evidence trail must come from running the actual files in `scripts/`, not from hand-rolled `python -c "..."` snippets that reproduce a weaker version of the check. The packaged checks are deliberately stronger than an obvious inline rewrite: `heterogeneity_check.py` uses token-overlap (not exact string match) plus the veto-reason test, and `lint_output.py` detects phantom `[E-...]` citations with no ledger row — both catch failures an inline reimplementation silently passes. A run whose "script log" is inline snippets satisfies the letter of the contract while defeating its purpose, and counts as **INVALID**. Use the exact commands below and pass files matching the schemas (full schemas and exit codes in `scripts/README.md`). Write JSON as plain UTF-8; the scripts tolerate a BOM, so a Windows `Set-Content -Encoding UTF8` file is fine.

- **`python scripts/heterogeneity_check.py roster.json`** — end of Phase 1, before construction. `roster.json` = `{"roles": [{"name","red_line","criteria","is_outsider","veto_reason"}...], "roster_review": {"shared_assumption_named": "...", "regenerated": false}}`. Note `criteria` is a **string**, `is_outsider` a **boolean**, and the review uses `shared_assumption_named` (not a bare `shared_assumption_checked`). Compares every pair on red lines and criteria by token overlap, runs the veto-reason test, and refuses to pass without a paradigm outsider and a named shared assumption. Exit 1 ⇒ regenerate the roster.
- **`python scripts/score_options.py options.json`** — Phase 5. `options.json` = `{"mode":"weighted", "criteria":[{"name","weight"}...], "options":[{"name","scores":{<criterion>:<1-5>}}...]}` (or `{"mode":"rice", "options":[{"name","reach","impact","confidence","effort"}...]}`). Computes composites and ranks. The ranking is input to the Approver, not a verdict; open disagreements are preserved.
- **`python scripts/lint_output.py deliberation.md [--interest-heavy]`** — before finalizing. Flags phantom `[E-...]` citations (cited but never defined in an evidence-ledger row), conclusions with neither an evidence anchor nor a `prior-only — unverified` tag, missing verification-boundary or honesty sections, and (with `--interest-heavy`) a reality wall not run per person. So an `[E-T1.1-1]` that points at no ledger row is caught here, not waved through.

If a script exits non-zero for a *data* reason (bad schema, unreadable file), fix the input and rerun — do not fall back to an inline check. `scripts/README.md` documents inputs, exit codes, and worked fixtures.

## References

References are phase-gated (read-when), not always-read. SKILL.md is enough for Minimal and for Stage 0 reject. In EXECUTE states, opening a reference is part of the evidence trail and counts against the depth ceiling; in REASONING-ONLY, cite which were used. Also: `references/skill-handoff.md` (read-when: sibling domain).

- `references/execution-substrate.md` — the substrate in depth, the adaptive-entry detail, the full single-model mitigation protocol, tool-by-role-and-phase allocation, and cross-model handling.
- `references/role-generation.md` — axis-selection procedure, the role-card template, the mandatory guard and outsider cards, the machine-checkable roster schema, and the full heterogeneity check.
- `references/facilitation.md` — run-scripts for the collaboration methods (NGT, Delphi, subgroups) and the facilitator's per-phase checklist.
- `references/retrieval-and-evidence.md` — efficient retrieval by role and phase, source tiering, anchoring discipline, and the evidence-integration ledger.
- `references/prompts.md` — copy-paste engine-switch prompts and the single-model mitigation prompts.
- `references/worked-examples.md` — calibration examples (rejection gate, roster regeneration, per-person wall, chaos gate, both-axes compression, psychological safety, cross-border compliance, pseudo-diversity trap) and the problem-type routing matrix.
