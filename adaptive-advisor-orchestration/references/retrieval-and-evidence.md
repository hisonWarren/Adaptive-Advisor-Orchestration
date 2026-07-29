# Retrieval and Evidence

For the roles that carry retrieval — by default the reality wall and the paradigm outsider, not every role. This is the mechanics of external-evidence anchoring, which is the single-model user's substitute for cross-model heterogeneity: external evidence is the one input that does not come from the model's own prior.

Core rule: retrieval is by role and phase, not blanket. Arming every role doubles cost and lets low-quality results pollute judgment. Every retrieval call needs a one-line reason — "why this step needs external evidence." No reason, no search.

## Who searches, for what

| Role | Searches for | Does not search for |
|---|---|---|
| Reality wall | Real-world outcomes of comparable cases; actual failure and adoption rates; real constraints (cost, regulation, timelines) | Abstract theory |
| Paradigm outsider | How the adjacent field handles this class of problem; cross-domain evidence that breaks the native frame | The problem's own literature, which reinforces the frame |
| Domain builders | Nothing by default — pure reasoning; searching front-loads noise into construction | — |
| Adversary | Only to falsify a specific claim ("under condition X this is wrong — has anyone observed X?") | General support for a position |
| Facilitator | Nothing — it integrates others' evidence | — |

## Efficient query design

Keep queries short and specific, one to six words; start broad, then narrow. One query equals one claim — do not bundle, since a bundled query returns shallow results for all of it. Use the real current year or omit it. On a miss, reformulate with different terms, a different source, or a different angle rather than repeating the same phrasing. For a load-bearing claim, fetch the full source rather than resting on a snippet.

## Source tiering

Prefer original, primary, authoritative sources; discount aggregators and SEO-heavy content.

| Tier | Sources | Use |
|---|---|---|
| A (anchor) | Peer-reviewed papers, primary data, official statute or standard, methodology originals | Load-bearing claims may rest here |
| B (support) | Reputable organizations, primary reporting, established practitioner writing | Corroboration |
| C (signal only) | Aggregators, forums, marketing pages | Leads to chase, never the final anchor |

Search more and believe less in skepticism zones: contested political or empirical topics, conspiracy-prone areas, heavily SEO'd domains like product recommendations. When results conflict, run more searches rather than picking the convenient one.

## Anchoring discipline

Every consequential claim from the adversary or wall should be checked against something external, then tagged `[E-Tn.m-k]`. A claim with no external anchor is marked "prior-only — unverified" and is not laundered into a finding — this is the honest terminus that separates grounded output from confident hallucination. Same-model agreement is not external anchoring: re-asking the model is not a check, only an external source or a human is. Respect copyright — paraphrase, keep quotes under fifteen words, one quote per source at most.

## Evidence-integration ledger

Owned by the facilitator whenever any role has searched. Its job is to turn scattered hits from multiple roles into one de-duplicated, source-tagged ledger keyed to the numbered issues, so every conclusion can point to its support.

| ID | Claim (paraphrased, <15 words) | Tier | Source | Supports | Conflicts? |
|---|---|---|---|---|---|
| E-T1.1-1 | example: the practice inflates the error rate | A | Author Year | T1.1, T3.3 | — |

Rules: one claim per row, paraphrased. De-dupe — if two roles found the same fact, it is one row listing both sources, not two rows that look like "strong evidence." Tier every row; a load-bearing conclusion rests on a Tier-A row or is marked unverified. Flag conflicts explicitly — a disagreement between sources is a finding, and a load-bearing one becomes a preserved open item in convergence, with a trigger for what would resolve it. Never cite a ledger ID that does not exist; if uncertain about a source, omit the claim rather than invent an attribution.

## Failure modes

Blanket arming (every role searches → cost blow-up and noise). Search-as-confirmation (search to falsify or to ground reality, not to comfort a held position). Snippet-citing a load-bearing claim. Prior laundering (presenting a prior-only claim as externally verified). Duplicate inflation (one fact listed three times looks like strong evidence but is one fact). Silent conflict resolution (dropping the source that disagrees). Phantom citations pointing to nothing.
