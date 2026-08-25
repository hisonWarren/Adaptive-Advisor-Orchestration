# Contract details

Read-when: Standard/Full when the always-loaded SKILL.md is not enough.
Hard constraints stay in SKILL.md and eval_lab/contract.json.

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

## Heterogeneity protocol

The deepest risk of any multi-role method is pseudo-diversity: different labels, same prior. Run this after role generation and before construction.

1. **Red-line / criteria pairwise check.** For any two roles, do red lines differ? Do evaluation criteria differ? If both match, merge.
2. **Veto-reason test.** Imagine each role voting against the same draft. Would the reasons differ? Three identical veto reasons means pseudo-diversity — regenerate.
3. **Independent sampling.** Generate roles in separate passes when possible, not one shot; one-shot listing lets later roles accommodate earlier ones.
4. **Adversary roster review.** Find one assumption no role would challenge. If found, the roster fails. **Name the shared assumption explicitly**; if regenerating, state what changed. Never mark "pass" without naming the assumption checked — an empty pass is theater.
5. **Paradigm outsider present.** At least one role that rejects the native terminology, not the speaker's life.
6. **Smooth-consensus watch.** Fast unanimous agreement is a danger signal; introduce sharper opposition or a human checkpoint.

Multi-agent debate only beats repeated single-agent sampling when genuine perspective differences exist; heterogeneity must be constructed and verified, not assumed. On a single model instance, all roles — adversary, wall, and outsider included — share weights and the same sycophancy bias, and a model cannot reliably self-correct its own reasoning from its own feedback. Structural gates reduce this but cannot remove it. The realistic mitigations are the single-model protocol in `references/execution-substrate.md` (review the artifact cold as external input, anchor claims to external evidence, keep prompts stance-free, use independent sampling to surface variance rather than to confirm) plus a named human backstop. Cross-model generation helps most but is an opportunistic bonus, not an assumption. **Same-model agreement is never evidence of correctness — only of shared prior.**

## Six-phase workflow

The rhythm is heavy construction → heavy critique → reconstruction. Let options form before attacking, then land them in reality. Copy-paste engine-switch prompts for each phase are in `references/prompts.md`.

**Phase 0 · Qualification.** Run Stage 0. Output: problem statement + speaker card or `situated: unspecified` + applicability verdict.

**Phase 1 · Role generation.** Axis selection → decompose → fill role cards. Add the two hard guards plus at least one paradigm outsider. Decide second-order as checklist or role (role only if >7). Run the full heterogeneity protocol including the adversary roster review. Apply panel-size rules. Output: roster + completed cards.

**Phase 2 · Construction.** Domain and stakeholder roles propose and build options boldly, no pre-critique. Adversary (after roster review) and wall stay mostly silent — keep the suits out. End with an axis-coverage check: do candidates cover different angles, or micro-tune one? Output: candidate options.

**Phase 3 · Adversarial round.** Adversary: steelman → attack the core → pre-mortem with the feedback-loop probe. Wall: four question classes plus the reality gate, per affected person on interest-heavy problems. Critique only — no patching this round; target core assumptions, not polish. Output: core criticisms + reality-gate results.

**Phase 4 · Reconstruction.** For each surviving criticism, reconstruct or consciously accept it as a constraint. Pointing out problems without a reconstruction path is forbidden. The wall re-checks reconstructed options: can real humans do this now, within tolerance? Options failing the reality gate are downgraded or dropped. Output: reconstructed viable options.

**Phase 5 · Convergence and accountability.** Numeric prioritization (RICE / weighted multi-criteria / Multi-Voting / MoSCoW). Explicitly separate full consensus, partial consensus (who aligns with whom), and genuine unresolved disagreement. Do not force-merge genuine disagreement — log it as an open item. The human Approver decides under DACI. Output: ranked options + decision record.

**Phase 6 · Second-order review and stop.** Run the second-order checklist. Stop when marginal benefit drops below cost — if direction is stable, key risks are identified, and further rounds would add noise, stop.

## Honesty discipline

1. Roles are thinking structures, not human experts. High-risk domains — clinical, legal, financial — require real expert review.
2. Single-model residual bias is irreducible by structure alone, and sub-agents do not fix it. Same-model sub-agents give context isolation and real tool execution but share the prior, and the model cannot reliably self-correct from its own feedback. Since cross-model is rarely available automatically, the working mitigation is the single-model protocol: review the artifact as external input, anchor consequential claims to external evidence, keep prompts stance-free, use independent sampling to surface variance rather than confirm, and name the human backstop for what stays unverified. Reach for agent orchestration to get real tool execution and context isolation, not to manufacture diversity.
3. Do not claim "validated" or "optimal." The output is multi-perspective reasoning, not proven reality. On "optimal," target the attainable frontier — each retained choice should survive real alternatives, residual limits are labeled, and you stop when marginal improvement costs more than it returns.
4. The human Approver owns the final judgment, always.
5. The method can become its own lock-in. Periodically ask where it was run mechanically and which decisions should have skipped it. The Stage 0 gate exists for this.
6. Checklist theater is worse than a single honest perspective. Each phase output must be concrete and externally auditable. If the adversary's criticism does not discomfort the designer, it is not working.
7. Pseudo-diversity cannot be fully tested — surface-different red lines may still share a deep prior. Mitigate as in point 2.

## Anti-patterns

Too many roles for a simple task. A fixed roster reused for every problem. Making the guards adaptive so the model can omit or soften the adversary. Merging the adversary and reality wall, which attack different failure modes. Role chatter with no decision impact. Treating smooth unanimous agreement as success. Compromise with no owner (missing DACI). No explicit decision criteria or numeric prioritization. No deferred trigger on open items. Running the full six phases on clear or chaotic problems. Endless rounds chasing "optimality" past diminishing returns. Marking heterogeneity "pass" without stating the shared assumption checked. Simulated compliance sign-off without an expert-review slot on regulated topics. The adversary attacking a real named colleague's character in a team-conflict setting. Making the adversary a standalone "only-objects" agent in an endless angel-versus-devil loop — it runs steelman → attack → reconstruction once and hands back. Using same-model multi-agent to fake heterogeneity — it is one prior in N hats; for real heterogeneity go cross-model or human. Reproducing the packaged scripts as inline `python -c` snippets to manufacture an exit code while skipping the stronger real check — call the files in `scripts/`, or declare REASONING-ONLY. Recasting a situated speaker into a stock persona to sound accessible. Inventing a biography on a task that is not first-person or public.

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
