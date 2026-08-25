# Guards runbook

Read-when: Phase 1–4 when running adversary / wall / outsider.

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
