# Worked Examples and Routing

Calibration anchors — concrete patterns to gauge gate strictness and output depth, not prescriptive answers. Below the examples is a routing matrix that picks axis, output depth, and panel size in one pass.

## Rejection gate (clear context)

"Standard CRUD app — Postgres or MySQL?" Best practice exists (Postgres is the default for most greenfield CRUD) and risk and uncertainty are both low. Gate: reject the panel. Recommend Postgres or the org standard, and note exceptions (a legacy Oracle team, a specific license constraint).

## Roster fail, then regenerate (domain-heavy)

A first roster of deployment expert, data-consistency expert, latency expert, migration expert, and team-cognition expert — all engineers sharing a "scale means microservices" prior. The adversary's roster review finds the shared blind spot: all assume the bottleneck is architecture, and none will question whether the real problem is uncached hot paths. Regenerate: keep at most two domain roles, add a paradigm outsider (an SRE who reverted microservices back to a monolith, speaking in operational load per engineer rather than service boundaries), and add a cost or accountability lens if the interest axis is weak.

## Interest-heavy wall, per person

Early-stage parent care — cohabitation versus a professional facility. The wall runs separately for the parent (autonomy and dignity), the spouse (household load), and the future self at year two (burnout sustainability). The same option may pass for one person and fail for another, which surfaces the trade-off for the Approver rather than producing a false "universal pass."

## Chaos gate (act first)

"Production is down right now — rollback or hotfix forward?" Chaos context: immediate action required, causal chain unclear, decision window closing. Gate: reject the panel. Output triage steps (stabilize → rollback if faster → communicate → post-mortem later). The panel runs after order is restored.

## Both-axes compression

A 200-person company adopts a four-day work week. Crossing the axes can generate eight or more roles (employee, middle manager, client, finance, HR, plus scheduling, productivity metrics, legal). Compress before construction: merge overlapping domain voices, keep one role per conflicting interest plus the guards and outsider, target ≤7 active voices, and use subgroup docs if still above seven.

## Psychological safety (team conflict)

"A team lead and a senior dev keep clashing over code-review style — should we mandate pair programming?" The ask is interpersonal plus plan, so it is interest-heavy with safety mode on. Reject if the user only wants a verdict on who is wrong. The adversary attacks the "mandate pair programming" option, not either person's character. The wall represents junior devs who won't speak up in pairs and the tech lead who loses async review time. The irreplaceable step — a facilitated retro with both parties — is not a simulated mediator's judgment on blame.

## Cross-border compliance

"A SaaS with EU and China users — single AWS region or split deployment?" Trigger expert-review slots: GDPR counsel, PIPL or local counsel, a DPO. The paradigm outsider is an air-gapped intelligence analyst ("you're optimizing uptime, not lawful basis and access path"). The adversary's finding: a single region plus encryption often fails audit on the access path, not on cipher strength — unpatchable without an architecture change. Blocker until expert review: whether China user data may legally transit or be processed in the proposed region. No faux Approver decision on legal permissibility.

## Pseudo-diversity trap (surface-different red lines)

A trap roster of "security hawk", "pragmatic engineer", "user advocate", "business growth", "tech-debt guardian" — red lines worded differently but all accepting "more features faster is good." The veto-reason test exposes it: all five veto "slow down releases" with different wording. Regenerate by replacing at least two with structural conflict — an on-call maintainer (stability), finance (CAC payback), an outsider (hospitality ops: "guests don't care about your sprint velocity"). Log it: heterogeneity regenerated, the shared prior was "velocity good," added stability and unit-economics voices.

## Problem-type routing

Use this after Phase 0 to pick axis, output depth, and panel size in one pass.

| Context | Gate | Primary axis | Output depth | Panel note |
|---|---|---|---|---|
| Clear + low risk | Reject | — | One-paragraph recommendation | No panel |
| Chaos | Reject | — | Triage action list | Panel deferred to post-incident |
| Complicated + domain | Proceed | Domain (+ outsider mandatory) | Standard | Watch pseudo-diversity; roster review critical |
| Emergent + interest | Proceed | Interest (+ per-person wall) | Standard or Full | Never collapse stakeholders into "the user" |
| Complicated/emergent + both | Proceed | Cross axes → compress to ≤7 | Standard | See both-axes compression |
| Any + time pressure | Proceed | As above | Minimal | Guards non-negotiable |
| Small scope (≤3 perspectives) | Consider reject | Known root cause | Minimal or skip | 1v1 beats a ceremonial panel |
| Real team conflict + low safety | Proceed with safety mode | Interest; critique plans not people | Standard | Reject if pure blame adjudication |
| Legal / cross-border / regulated data | Proceed + expert-review slots | Domain + interest | Full or Standard | Blocker until licensed review |
| Suspected pseudo-diversity | Proceed | Rerun Phase 1 | Standard | Veto-reason + roster review mandatory |

Academic and research decisions — methodology, instrument choice, analysis pipeline, collaboration structure — usually map to complicated and domain-heavy, with an interest axis added when advisor, committee, or funder incentives conflict. Treat the committee or PI as the Approver, not a simulated role.
