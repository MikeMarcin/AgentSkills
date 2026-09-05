---
id: ASK-0007
title: Refresh implement-rfc from SampleReview
status: In Progress
rfc: RFC-ASK-0001
depends_on: ["ASK-0004"]
---

# ASK-0007: Refresh implement-rfc from SampleReview

## Objective and owned paths

Import the latest local SampleReview skill changes into the canonical shared
skill while retaining the completed shared-consumer adaptation. Own
`skills/implement-rfc/**`, `docs/development/skill-provenance.md`, and this card.
SampleReview is read-only; consumer configuration and MASK state are outside
this refresh.

## Bounded work and acceptance

- Import SRV commit `c609655bc615e79e8e17eefc198c89861de0d90f`'s validated
  issue-board commands, schema, reference and tests.
- Preserve explicit external consumer resolution, fixture isolation, and safe
  adapter rendering. Keep inherited SRV facts only in the historical example.
- Verify changed board/config helpers, source validation and the public CLI
  through shared links with two different disposable consumers.
- Record provenance and regenerate only the portable source manifest.

## Verification and run record

RFC_BASE_SHA: d7d316700bcded466f02f8f20e5c473f47cf3ed1

This follow-up preserves the original RFC closeout and its historical evidence.
Focused checks and actual results will be recorded here before completion.
