---
schema: implement-rfc.card.v1
id: ASK-0018
title: Explicit implementation routing and local Codex/Claude role audit
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0014"]
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"54dcc05d33693261e3944760aa09bb6770a29643","evidence":{"kind":"observation","detail":"Reviewed the shared entrypoint, assignment contract and both worker definitions: routine preferred when eligible, deep requires concrete reason, direct trivial work preserved."}},{"criterion":"AC2","outcome":"pass","revision":"54dcc05d33693261e3944760aa09bb6770a29643","evidence":{"kind":"observation","detail":"21 audit tests and read-only native Codex/Claude scans passed; runtime activity identity and units, unknowns and partial coverage are explicit."}},{"criterion":"AC3","outcome":"pass","revision":"54dcc05d33693261e3944760aa09bb6770a29643","evidence":{"kind":"observation","detail":"Companion-attempt isolation fixture and 10 existing companion tests passed; documentation states execution cannot be inferred from a launch record."}},{"criterion":"AC4","outcome":"pass","revision":"54dcc05d33693261e3944760aa09bb6770a29643","evidence":{"kind":"observation","detail":"Two linked-consumer public CLI fixtures, actual Codex/Claude CLI smoke checks, 11 adapter tests, source manifest and skill validation passed; native Windows/remote execution limitations recorded."}}]
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

## Verification and implementation

Implementation: `54dcc05d33693261e3944760aa09bb6770a29643`.

- `python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_role_usage.py`: 21 passed, including two separate consumers invoking the public CLI through shared links, explicit project/role filtering, timezone boundaries, inherited-history exclusion, response deduplication, partial/corrupt coverage, quoted-banner exclusion, unknown model/effort and launch-attempt separation.
- `python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_render_runtime_adapters.py`: 11 passed; both native providers render correctly in temporary consumers.
- `python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_codex_lane.py`: 10 passed with the fake companion; all role routes retained.
- `validate_portable_agents.py --source-only`, skill-creator `quick_validate.py`, and `git diff --check`: passed after portable manifest regeneration.
- Read-only native Codex/Claude scan for September 5 PDT: no coverage issues; Codex routine worker 1 new/1 active/1 turn, Sol/high; no retained Claude activity that date. Codex counts include this audit's reviewer and other concurrent work.
- Public Claude CLI for August 16 UTC: exit 0, 54 active agents, 1,612 distinct responses, seven reported native types, no coverage issues.
- Public Codex CLI via ManageAgentSkills' shared skill link with `--driver codex --date 2026-09-05 --timezone America/Los_Angeles --role rfc-worker-routine`: exit 0 and the same routine-worker result.

One independent read-only forward-test used synthetic histories. Its three
concrete findings (pretty-printed metadata, invalid/empty timestamp coverage,
and quoted identity examples) were corrected and exercised by regression tests.
No second review or repeated unchanged verification was required.

Native Windows execution and remote/companion model execution were not exercised.
The audit uses UTC without optional IANA data; Windows path comparison is covered
by fixtures. Companion logs explicitly describe attempts only. Historical routing
reasons remain unknown. Consumer adapter regeneration and cached-host reloads
were not performed across other projects; delegations now explicitly ask workers
to echo the choice, and future adapter renders include the same instruction.

All disposable fixtures were cleaned up; no local transcripts were copied into
the repository. No MASK/runtime state, consumer settings, credentials or remotes
were changed. The initial structure gate detected this open follow-up attached
to its completed RFC; rerun after terminal bookkeeping below.

Final structure gate after finish `c7c55dae0ea98b5ad97343ed7c7614be724d4ff1`: `python3 -B scripts/verify_documentation.py --root .` passed (4 RFCs, 18 cards, zero violations). No remaining acceptance work.
