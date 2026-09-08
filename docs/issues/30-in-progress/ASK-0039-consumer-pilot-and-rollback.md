---
schema: "implement-rfc.card.v1"
id: "ASK-0039"
title: "Deploy a scoped cross-project pilot with reversible bindings"
status: "In Progress"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0026", "ASK-0036", "ASK-0038"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "consumer-pilot-and-rollback"}
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

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
