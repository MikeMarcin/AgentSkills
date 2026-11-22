---
schema: "implement-rfc.card.v1"
id: "ASK-0139"
title: "Route visual art approvals through the attended review hub"
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"433ad418a19e336987f7109e448fcdb96cd2c1c1","evidence":{"kind":"observation","detail":"Disposable MASK consumer installed agentskills/art-review from the committed Git source. Both skills matched the canonical files under both discovery adapters. Skill validation and documentation checks passed."}},{"criterion":"AC02","outcome":"pass","revision":"433ad418a19e336987f7109e448fcdb96cd2c1c1","evidence":{"kind":"observation","detail":"Five real submitted concepts were matched to all five human outcomes from the configured hub. The original visual manifest validated the resulting verdict. Five source tests passed, including refusal of missing, changed, wrong-session and post-handback decisions and changed source bytes."}}]
---

# Route visual art approvals through the attended review hub

The concept-art pipeline sends human reviewers to a checkout-local HTML file. Require the attended-review companion for hosted visual decisions, pair the skills for deployment, and retain offline exports for explicitly offline work or a reported transport failure. Preserve each art candidate's source identity and consume the reviewer's saved handback without requiring a second decision.

## Acceptance

- **AC01** A driver can select the two skills together and find the hosted, offline, and autonomous review paths.
- **AC02** The attended handback maps real decisions and notes to their exact art batch, gate, candidates and media. A partial or stale handback cannot approve the full batch.
