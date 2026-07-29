# Facilitation

Run a high-quality panel with mature meeting methods. The facilitator is a function, not a domain voice: at Floor and Mid tier it is the executing model wearing a facilitation hat; at High tier it can be a dedicated orchestrator agent.

Prime directive: the facilitator's success is decision quality plus preserved disagreement, not consensus. If the meeting ends smoothly unanimous, the facilitator has likely failed — smooth consensus is a danger signal. Steering toward agreement, suppressing a dissenting role, or summarizing away a genuine open item are all forbidden.

## Method by panel size

| Size | Method | Why | Script |
|---|---|---|---|
| ≤3 | 1v1 / tight round-robin | Formal structure is overhead | Each speaks once, adversary attacks, converge |
| 4–7 | Nominal Group Technique | Prevents first-speaker anchoring | Silent independent generation → round-robin share → clarify → vote |
| 8–12 | Delphi (2 anonymous rounds) or Six Thinking Hats | Anonymity cuts conformity and authority pressure | Round 1 anonymous positions → aggregate → round 2 revise → converge |
| >12 | Subgroups + structured inter-group docs | Large groups collapse into noise | Split ≤5 per group → each produces a doc → cross-read → plenary decision |

The default for a 4–7 voice panel is NGT, and the reason matters here specifically: the method's deepest risk is pseudo-diversity, and NGT's silent independent generation before any sharing is a structural defense against roles anchoring on whoever spoke first.

## NGT run-script (the default)

Each step has an explicit start and stop so the phases do not blur.

1. **Silent independent generation.** Each role produces its position without seeing the others'. In a single-model run, enforce this by generating each role in a separate pass, prompting it only with the problem statement and its own card — never the other roles' outputs yet.
2. **Round-robin share.** Collect all positions. No cross-talk or rebuttal yet — surface everything so nothing is anchored out.
3. **Clarify, don't persuade.** Only clarifying questions. Watch the second-order signals: is anyone echoing another role? Whose position comes from tone, not evidence?
4. **Adversary roster review.** Attack the panel itself — name one assumption none of the roles would challenge. If found, the roster fails; regenerate rather than voting on a homogeneous panel.
5. **Construction round.** Roles build options together; adversary and wall stay mostly silent so options can form.
6. **Adversarial and reality round.** Adversary: steelman → attack → pre-mortem. Wall: per-affected-person load test. Critique only, no patching.
7. **Reconstruction and convergence.** Reconstruct surviving criticisms; numeric prioritization; explicitly separate consensus, partial consensus, and genuine open disagreement.
8. **Decision slot and second-order check.** Human is the Approver. Run the checklist. Preserve open items with triggers.

## Per-phase second-order checklist

Run at the end of each phase (a checklist, not a role slot, unless the panel exceeds seven):

- Did we lock into a frame too early?
- Did we agree too smoothly? If yes, inject sharper opposition or flag for the human.
- Is any role repeating another without new reasoning?
- Whose stance comes from tone rather than evidence?
- What unstated premise did we all assume?

## Failure modes

Consensus-chasing (a real open item is a success, not a loose end). The angel-versus-devil death loop (the adversary runs steelman → attack → reconstruction once and hands back). Flattening stakeholders into one generic "user" (run the wall once per affected person whose tolerances conflict). Efficiency over heterogeneity (if organizing the meeting well costs a real disagreement, it optimized the wrong thing).

## High tier note

A dedicated orchestrator agent dispatches roles as context-isolated sub-agents (isolation is the real gain — it reduces cross-role anchoring), routes tools by role and phase rather than giving every agent every tool, and must return a "preserved open disagreements" section — an orchestrator that returns only consensus is malfunctioning. If the harness declares cross-model, assign a different model family to adversary and outsider than to builders; the orchestrator cannot self-detect this, so it must be declared.
