---
schema: "implement-rfc.card.v1"
id: "ASK-0122"
title: "Use medium effort for Claude implementation defaults"
status: "Done"
rfcs: []
depends_on: []
metadata: {"baseline":"f8e70fd","execution_strategy":"direct","requested_on":"2026-10-22","remapped_from":["ASK-0111","ASK-0121"],"remap_reason":"Never published. Upstream assigned ASK-0111 and then ASK-0121 to other work before this landed, so it was reapplied onto current main with newly reserved ASK-0122."}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"b1b3213c1979c124edc588001d5e47bee4c1b48f","evidence":{"kind":"command","detail":"30 of 31 focused native adapter, execution strategy and host tests pass with PYTHONUTF8=1; generated Claude frontmatter and banners request Opus 5.5 medium for implementer and worker. The one failure, test_attended_review_is_a_watched_fresh_context_boundary, fails identically on unmodified upstream f8e70fd."}},{"criterion":"AC2","outcome":"pass","revision":"b1b3213c1979c124edc588001d5e47bee4c1b48f","evidence":{"kind":"artifact","detail":"Active routing and selection references record the dated owner-directed medium trial, the existing medium worker default and the unmeasured quality and host-loading limits."}},{"criterion":"AC3","outcome":"pass","revision":"b1b3213c1979c124edc588001d5e47bee4c1b48f","evidence":{"kind":"command","detail":"Portable manifest changes exactly the four edited files' hashes and the digest, in canonical POSIX order; the method reproduces upstream's prior digest. Documentation gate and diff checks pass in a clean LF worktree."}}]
---

# Use medium effort for Claude implementation defaults

The owner wants to try medium effort for the default Claude Code implementer and
standard worker after feedback from Anthropic. The standard worker already uses
medium; lower the independent implementation class from high to medium.

Own `skills/implement-rfc/config/routing.json`, its active routing and selection
references, the existing native adapter expectation and the portable manifest.
Preserve other model routes, permissions, role authority and historical evidence.
This is a source change; consumer deployment and live model evaluation are
outside scope.

Acceptance:

- AC1: Both Claude roles request Opus 5.5 medium in canonical configuration,
  generated native settings and startup banners; all other routes match baseline.
- AC2: Active documentation records the owner's trial and distinguishes it from
  measured quality or directly verified provider feedback.
- AC3: Focused adapter tests, portable-source validation, documentation validation
  and diff checks pass without including unrelated source changes.

Native host loading and quality at the new effort remain unmeasured.

## Verified result, 2026-10-24

Source revision: `b1b3213c1979c124edc588001d5e47bee4c1b48f`, on upstream `f8e70fd`.
Routing changes only the Claude implementation effort and the review date.

The work was first done on 2026-10-22 as ASK-0111 and then ASK-0121, on a local
branch that was never pushed. Upstream took both IDs for other cards before it
landed. The same skill edits were reapplied onto current main without conflict
and the card was renumbered to ASK-0122. The original history is kept in the
owner's local branch `local/claude-medium-effort-2026-10-22`.

In a clean LF worktree, `python -B -m unittest test_render_runtime_adapters
test_execution_strategy test_strategy_host` ran 31 tests with `PYTHONUTF8=1`:
30 pass. `test_attended_review_is_a_watched_fresh_context_boundary` expects the
removed recipe text `start its loopback HTML server` and fails the same way on
unmodified upstream; this card does not repair it.

The portable manifest was not written with `--write-source-manifest` on Windows.
That path sorts `Path` objects case-insensitively there, which reorders entries
and changes the digest. Instead the four edited files were rehashed in upstream's
existing POSIX order. That method reproduces upstream's previous digest
`de55d2919f8a9b04` and gives `8a7b605df8ee23cb`.

Closeout review runtime: primary-session self-review; direct execution, no subagents.
