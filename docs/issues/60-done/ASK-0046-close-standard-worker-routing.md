---
schema: "implement-rfc.card.v1"
id: "ASK-0046"
title: "Integrate and close the standard-worker routing change"
status: "Done"
rfcs: ["RFC-ASK-0009"]
depends_on: ["ASK-0045"]
closeout_for: ["RFC-ASK-0009"]
metadata: {"packet":"agent-skills-standard-worker-review", "provisional_id":true}
acceptance: [{"criterion":"RFC-ASK-0009-AC01","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"Primary semantic review of all 13 retained selection cases, SKILL/roles/delegation prompts; test_standard_worker_target and unified-workflow checks; full commands/results and rebase mapping retained in closeout."}},{"criterion":"RFC-ASK-0009-AC02","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"Exact target checker (owner rename applied in memory), native renderer and fake companion forwarding; both-provider standard/deep/reviewer independent overrides; full commands/results and rebase mapping retained in closeout."}},{"criterion":"RFC-ASK-0009-AC03","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"9 test_role_migration cases: hash/ownership collisions, linked retirement, pure check, repeat, interrupted retry, frozen orders, addenda and clean prior snapshot restore; pending launch guards; full commands/results and rebase mapping retained in closeout."}},{"criterion":"RFC-ASK-0009-AC04","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"22 test_role_usage tests, including raw old/new/generic unknown roles, deduplicated decisions and unknown effort; usage capture/scope/CLI checks; full commands/results and rebase mapping retained in closeout."}},{"criterion":"RFC-ASK-0009-AC05","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"69 integration-focused tests plus focused suites below; source-only manifest validation; integrated structure gate: 9 RFCs, 46 cards, 0 violations; full commands/results and rebase mapping retained in closeout."}},{"criterion":"RFC-ASK-0009-AC06","outcome":"pass","revision":"18e861136df3448e1c5c30572a63bd520d0cb183","evidence":{"kind":"observation","detail":"role-adoption.md and active routing/docs reviewed; MASK observational capabilities/config/source status/project show; no native/quality/cost claim; full commands/results and rebase mapping retained in closeout."}}]
---

# ASK-0046: Integrate and close the standard-worker routing change

Governing RFC: [RFC-ASK-0009](../../rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).

Criterion coverage: RFC-ASK-0009-AC01, RFC-ASK-0009-AC02, RFC-ASK-0009-AC03, RFC-ASK-0009-AC04, RFC-ASK-0009-AC05, RFC-ASK-0009-AC06.

## Objective and owned paths

Sole closeout for RFC-ASK-0009. Own this card, the new RFC/status/index row, and the
small live import/adoption record. Preserve all older RFCs, cards and retained evidence.

## Work and acceptance

Inspect the integrated scoped diff against the real RFC_BASE_SHA, consume one focused
review of changed policy/migration behavior where warranted, and reconcile all six
criteria. Confirm all three implementation cards are Done. Record effective target
settings and source revision separately from observed runtime execution. Run the
repository structure gate once at integration and missing/invalidated focused checks only.

Configuration adoption is owner-directed. A missing live quota comparison is a disclosed
limitation, not a blocker or a reason to claim a saving. Record any explicitly authorized
consumer adoption separately; leave unrelated projects, pins, sessions and paid usage
untouched. Document rollback and remove only task-created temporary fixture roots after
results are retained. No push or automatic registry-wide update.

## Durable closeout anchor

RFC_BASE_SHA: 52aa2bb016d92b3d3fc881a8e6b4c2d1390df900

Capture the actual pre-source-work Git SHA at intake; the pack cannot supply it.
Planned cards: ASK-0043, ASK-0044, ASK-0045, ASK-0046 (remap with live allocation).

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0009-AC01 | Primary semantic review of all 13 retained selection cases, SKILL/roles/delegation prompts; test_standard_worker_target and unified-workflow checks | Pass | 0cb20eb |
| RFC-ASK-0009-AC02 | Exact target checker (owner rename applied in memory), native renderer and fake companion forwarding; both-provider standard/deep/reviewer independent overrides | Pass | 18e8611 |
| RFC-ASK-0009-AC03 | 9 test_role_migration cases: hash/ownership collisions, linked retirement, pure check, repeat, interrupted retry, frozen orders, addenda and clean prior snapshot restore; pending launch guards | Pass | 18e8611 |
| RFC-ASK-0009-AC04 | 22 test_role_usage tests, including raw old/new/generic unknown roles, deduplicated decisions and unknown effort; usage capture/scope/CLI checks | Pass | 31fdb7d |
| RFC-ASK-0009-AC05 | 69 integration-focused tests plus focused suites below; source-only manifest validation; integrated structure gate: 9 RFCs, 46 cards, 0 violations | Pass | 18e8611 |
| RFC-ASK-0009-AC06 | role-adoption.md and active routing/docs reviewed; MASK observational capabilities/config/source status/project show; no native/quality/cost claim | Pass | 1ae1f40 |

## Limits and owner decision

Requested routes are selected by the owner in this conversation. Runtime serving,
model-quality equivalence and subscription savings are unmeasured by this pack.
Keep those statements distinct from the configuration acceptance above.

## Integrated evidence and review

Integrated source revision: 18e861136df3448e1c5c30572a63bd520d0cb183. Main fast-forwarded after a clean rebase over
concurrent unrelated commit 3e6d278 (source-dump tool and .gitignore). The immutable
RFC_BASE_SHA remains unchanged. `git diff --exit-code 2599970 18e8611 --
skills/implement-rfc docs/rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md`
passed, establishing unchanged tested source through rebase. Original card evidence
revisions remain historical; integrated equivalents are a67a867 → 0cb20eb,
1b1477a → 31fdb7d, e4f7157 → 1ae1f40, 2599970 → 18e8611.

Actual focused commands used `python3 -B -m unittest discover -s
skills/implement-rfc/tests -p NAME.py -q`: test_role_migration (9),
test_role_usage (22), test_codex_lane (11), test_unified_workflow (11),
test_slice_commands (13), test_slice_integration (9), all passed. One integration
invocation loaded test_render_runtime_adapters, test_standard_worker_target,
test_usage_capture, test_usage_scope and test_usage_cli with unittest (69 passed).
Total distinct tests: 144; unchanged passing evidence reused. No optional full
historical runtime matrix was run.

`python3 -B docs/rfcs/assets/agent-skills-standard-worker-review/tools/validate_pack.py`
passed: one RFC, four cards, 13 cases, zero violations. The target unittest invokes
that retained pack's checker with only rfc-critical-reviewer → rfc-reviewer-critical
applied to its fixture in memory; retained provenance bytes are unchanged.

At integrated revision above, `python3 -B scripts/verify_documentation.py --root .`
passed (9 RFCs, 46 cards, 0 violations),
`python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only`
passed, and `git diff 52aa2bb --check` passed. An earlier attempted fast-forward
refused due to the concurrent commit; checks on that pre-integration tree were
not treated as integrated evidence.

Closeout review runtime: primary Codex session, direct skeptical review; no delegated
or live provider review trial. Inspected the final scoped diff against RFC_BASE_SHA,
including parser history, override precedence, hash preflight, pending publication,
retired paths and authority guards. No known critical in-scope failure. Simplification
review kept deterministic preflight/publication in one renderer helper and existing
receipts; no new scheduler or collector. The sole final coverage correction added
explicit deep-worker override independence alongside standard-worker coverage.

Policy cases: ordinary multi-file/local design, approved wire/permission/lifetime
changes, unfamiliar packages and progressing diagnosis remain standard; conflicting
invariants and known difficult causal problems can start deep. Scope expansion goes
to the integrator, prescribed commands to the runner, small coupled edits stay direct,
quota errors follow explicit capacity policy, and a clean normal review does not
trigger a second review. Risk selects safeguards independently of worker difficulty.

## Effective requests and adoption boundary

| Role | Codex request | Claude request |
|---|---|---|
| rfc-utility, rfc-test-runner | gpt-5.6-luna / xhigh | claude-haiku-4-5 / unsupported null |
| rfc-scout | gpt-5.6-sol / low | claude-opus-5 / low |
| rfc-worker | gpt-6-astra / low | claude-opus-5 / xhigh |
| rfc-worker-deep | gpt-6-astra / high | claude-fable-5-1 / high |
| rfc-reviewer | gpt-6-astra / medium | claude-fable-5-1 / medium |
| rfc-reviewer-critical | gpt-6-astra / xhigh | claude-fable-5-1 / high |

Claude floor declared 2.1.255. Provider requests were rendered/tested with fake drivers;
actual serving, native reload, model quality and savings were not measured. Existing
primary settings, role mutation authority, turn limits and leaf boundaries are retained.

MASK read-only inspection found the canonical development source at a3bcb1a during
authoring, ahead/dirty with independent edits, and a schema-v1 AgentSkills consumer
using directory links without a selected pin. Integration deliberately activates
verified canonical bytes for development links. No live native adapters, other
consumer declarations, locks, sessions or MASK state were mutated. Adoption and
rollback are documented in skills/implement-rfc/references/role-adoption.md; external
native sessions require integrator inventory, beyond the local admitted-run check.
No remaining required human decision or implementation criterion is open.

## Cleanup

Temporary consumer fixtures used context-managed TemporaryDirectory roots and were
removed after checks. The task authoring worktree and temporary acceptance files are
removed after closeout; canonical/main is their only integrated consumer. Original
Downloads input and retained packet provenance remain. Concurrent source-dump changes
are preserved in their author's commit.
