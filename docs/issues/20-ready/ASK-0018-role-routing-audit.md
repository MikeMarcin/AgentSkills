---
schema: implement-rfc.card.v1
id: ASK-0018
title: Explicit implementation routing and local Codex/Claude role audit
status: Ready
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0014"]
---

# ASK-0018: Explicit implementation routing and local role audit

User-requested follow-up; preserve the original RFC closeout and evidence.
RFC_BASE_SHA: fbf9619c6e04489d9be34f802feb7248bc41db64

Own `skills/implement-rfc/` policy, role definitions, audit helper, focused tests,
portable manifest, and this card. No consumer migration or MASK runtime changes.

## Acceptance

- AC1: Substantial delegated implementation chooses routine/deep with a concrete
  reason, preferring routine when its established-pattern and verification
  prerequisites hold. Trivial work can stay with the primary; sensitive changes
  retain the deep route. No delegation quota or new acceptance gate.
- AC2: A maintained read-only CLI audits local Codex and Claude subagents by
  date, project and role, with observed model/effort, aggregate counts and source
  references. Distinguish native activity units, inherited history, repeated
  records, unknown identity and missing/corrupt coverage. No prompt/log dumps.
- AC3: Claude-driven Codex companion launch records remain separate attempts,
  never evidence that a model executed. Document explicit input selection and
  historical limitations, and retain missing routing reasons as unknown.
- AC4: Exercise both parsers and the public CLI with temporary fixtures,
  two consumers through shared links, and read-only local smoke checks. Validate
  skill/source structure and record exact outcomes without exporting transcripts.

## Routing

Deep: the cross-runtime parser and counting rules are a new design with no
established implementation pattern. Implement locally; no parallel writer needed.
