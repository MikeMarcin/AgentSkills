---
schema: "implement-rfc.card.v1"
id: "ASK-0039"
title: "Deploy a scoped cross-project pilot with reversible bindings"
status: "Done"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0026", "ASK-0036", "ASK-0038"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "consumer-pilot-and-rollback"}
acceptance: [{"criterion":"RFC-ASK-0008-AC05","outcome":"pass","revision":"be3f768057a06033569e99ab0253c646e6f168f1","evidence":{"kind":"observation","detail":"Two exact named managed consumers: guarded state-only MASK apply, candidate render/check and baseline rollback; protected config hashes and clean source trees preserved. Installed nested-cwd/registry dry runs pass. Separate public pinned-artifact fixture captured successfully and cleaned. Host first-prompt loading remains unclaimed."}}]
---

# ASK-0039: Deploy a scoped cross-project pilot with reversible bindings

Governing RFCs: [RFC-ASK-0008](../../rfcs/RFC-ASK-0008-routing-profiles-and-portable-rollout.md).

## Objective and owned paths

Select the actual consumer set explicitly (initially the measured SRV/SamplePlanner projects unless owner chooses otherwise). Use existing public MASK operations with guarded plans, preserve pins/dev-links and unrelated native configs, and record actual installed payload/profile digests. Prove opt-out and profile rollback prospectively without discarding edits or reports. Collection across registered projects is not permission to deploy across them.

Own only: `skills/implement-rfc/references/bounded-execution.md`; `skills/implement-rfc/references/usage-collection.md`; `selected deployment and rollback evidence references`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- The same canonical package works for distinct consumer contexts and pins; no per-project fork or upstream MASK code change is required.
- A user can collect the later experiment with one --mask-projects invocation and attach the resulting local archive.

Criterion coverage: RFC-ASK-0008-AC05.

## Focused verification

Run installed dry-run scope and one sample capture, then disable/re-enable only the pilot selection and inspect unchanged unrelated consumers. Record only actual host-load observations.

## Run record

Selected only SampleReview and SamplePlanner, the two consumers named by the accepted pack. Public MASK project.show/plan verified their existing managed shared links for both providers. Reviewed guarded apply operations recorded source state only (`state.record`); no bindings or project declarations changed and no other consumer was selected.

Before rendering, every existing generated adapter matched its prior ownership manifest. Captured hashes of project declarations, native config/settings and SamplePlanner's explicit routing override. Invoked the candidate explicitly on each consumer, checked it, then rendered/checked baseline again. SamplePlanner always used its required `--routing-override .mask/skill-config/implement-rfc/routing-override.json`; its Claude deep/review routes remained Opus as configured. Protected hashes stayed identical and both Git working trees remained clean.

| Consumer | Candidate source digest | Final baseline source digest |
|---|---|---|
| SampleReview | 7d19aefc9f8649469dd99404b7b3c0384672358bcbba8535672ce107ee746eab | 96b240fa44f4d19b0b8fb658cff33de7f4026528e451b568c53135354e76a1e7 |
| SamplePlanner | ae353d325619aa770e51d6d667003923255b7ba5072d9ebadc2b7ec81361ca5a | 81e5499d0599277d565dd707d32b0985786197d92435dd4c5ba4279bb04b2c24 |

Candidate profile digest: `141ee2dfcd5f774d4ca5272c71d8bf443e102c564007d3798dab3f0c9f9716e1`. These are requested configuration observations, not serving-model observations. Capability input used the available host model metadata for gpt-6-astra/low. No candidate model was launched and no primary-session setting changed.

Installed nested-cwd dry runs through SampleReview's `.agents` link and SamplePlanner's `.claude` link each selected the correct consumer. One public `--mask-projects --dry-run` invocation selected seven registered projects without deployment. Reused the unchanged real registry capture on ASK-0024 (400 sessions, partial coverage) rather than repeating its 43 GB scan.

A disposable local bare-remote/MASK fixture also exercised public register/require and guarded `migrate --to-pinned` plan/apply. The selected usage.py resolved inside MASK's pinned artifact store, not the authoring checkout, and ran successfully to a metadata ZIP with unchanged script SHA256 `de02ea60f0d4daaf002733b51dd1c383da854b8fd2fdc7be0ef697f5627dffd3`. Fixture source/store/consumer/bare remote and sample ZIP were cleaned automatically; no actual consumer was migrated to pins.

Rollback was prospective: both pilot adapters end at baseline, existing shared-source bindings remain, and private run reports/history survive. Host first-prompt loading is not inferred from these filesystem/helper checks; MASK continues to report host_load=not_verified. No publication, global settings, account changes, purchases, resets or additional model attempts occurred.
