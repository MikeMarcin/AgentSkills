# Source basis and limits

## Supplied source, not a live checkout

The principal implementation basis is the AgentSkills dump generated September 8,
2026 at 08:49:51 PDT: 298 included files, RFCs through RFC-ASK-0009, and NEXT_ID
ASK-0050. The latest supplied MASK dump is generated at 08:49:47 PDT and supplies
package/deployment boundaries, not authorization to modify its program. Exact raw
upload hashes and selected reconstructed file hashes are in
[source-basis.json](source-basis.json). Dump normalization loses some trailing blank
lines, so extracted-file hashes do not pretend to be exact full-tree Git evidence.
Live commits, subsequent edits, availability, reservations and consumer versions
must be reconciled by the importer.

The current supplied AgentSkills source already contains the context-reuse change
from the attached 0b6f786 patch. Its inverse describes the earlier usage run; it is
not the desired implementation baseline. Preserve that patch's correction/fresh
review boundaries rather than reverse it when adopting this new RFC.

## Decisions supplied by the owner

The conversation selects native interactive coordination over an external
supervisor because the owner prefers avoiding subscription-access dependencies.
This is an architectural preference, not this packet's provider-policy/legal
claim. The coordinator waits on a fresh milestone integrator; current-milestone
corrections reuse its context. The chosen coordinator routes are Opus 5 low and
GPT-5.6 Sol low, with Codex allowance conservation more important than nominal
cross-provider cost equality. Implementation quality is to be preserved.

## New design details in this packet

The distinct `rfc-integrator` role, session-only coordinator configuration,
independent integration defaults for previously unconfigured runs, exact return
contract, optional narrow sibling-review fallback and versioned schema migration
are implementation proposals. ROUTING.md labels the integration-default resolution
separately from the owner's explicit coordinator choices. Complete-slice ownership,
early composed milestones and conditional reference loading develop the accepted
direction; native efficacy and cost savings have not been demonstrated.

## Source-derived seams

| Source location | What it establishes |
|---|---|
| skills/implement-rfc/SKILL.md and references/delegated-execution.md | Existing primary-integrator authority, useful-parallel-primary-work trigger and correction/fresh-context policy that need active reconciliation |
| config/roles.json, config/routing.json and schemas | Seven existing leaf routes and limited delegation field; not an existing full integrator role |
| scripts/render_runtime_adapters.py | Guarded native output ownership, current leaf tool restrictions, per-role rendering; generated intent is not native execution |
| tests/test_standard_worker_target.py | Live test uses an exact historical target; extend the live test without altering retained historical assets |
| references/bookkeeping.md and consumer context | Explicit root, immutable RFC_BASE_SHA, allocation/reservation, focused evidence, staged-path and board contracts |
| references/pack-lifecycle.md and project rules | Current active handoff wording must respect no implicit push; reconcile conflict without changing historical work |
| scripts/usage_capture.py and usage_accounting.py | Existing older counter capture and reconciliation; newer owning response records need narrow support |
| scripts/usage_outcomes.py | Missing outcome input must be distinguished from measured zero; controlled experiment rules must remain strict |
| MASK package/adapter contracts | Plain portable frontmatter and passive package validation; host output belongs outside the shared payload; links/pins/host loading are distinct |

The supplied [writing-for-agents](reference/writing-for-agents/SKILL.md) and its
[mechanics reference](reference/writing-for-agents/SKILL-MECHANICS.md) are retained
as authoring sources, not new installed skills. They provide context pointers,
information hierarchy, ordered completion criteria, co-location, single-source
rules and pruning. Their host-specific invocation examples are not copied into
MASK's stricter portable frontmatter. The application is explained in
[WRITING_REVIEW.md](WRITING_REVIEW.md).

## Earlier audit: motivation, not a matched treatment

The previously delivered `codex_usage_deep_audit_2026-09-08/EVIDENCE.md` and the
attached SRV usage archive establish the motivation used here: 4,573 task-family
responses, about 575 million input tokens including repeated cached context, and
a primary responsible for about 38% of dated rate-equivalent cost. The roughly
16.1-hour allowance duration was an account-wide extrapolation, not a fully
observed isolated exhaustion. The original report documents coverage and quota
attribution limits. No new audit or revised financial estimate is asserted here.

Forty comparable productive hours would require a large improvement; neither
shorter instructions nor moving primary work to children proves it. The earlier
proposed SKILL and adoption notes are design inputs, not current source. This
packet supersedes their external/primary-rotation direction with the user's
native interactive coordinator decision. It preserves direct verification and
counts all integrator generations and repair work. Raw private transcripts and
account details are intentionally not bundled.

## Official runtime documentation checked September 8, 2026

These are external runtime facts, separate from supplied source and from observed
installed behavior. Recheck the installed version when qualifying the candidate.
The native host may change; the RFC specifies behavior rather than guessed flags.

**Codex subagents.** Native custom agents support model/effort/instructions and
spawn/continuation/waiting. Per-agent configuration precedence and inherited live
permission settings matter. This supports the proposed native design, but does
not prove the user's installed nested path. Source:
[Codex subagents](https://developers.openai.com/codex/subagents).

**Codex configuration.** Current reference documents agents.enabled and
max_concurrent_threads_per_session. Use the documented installed control rather
than assume another release's nesting option. Source:
[Codex configuration reference](https://developers.openai.com/codex/config-reference).

**Claude subagents.** Current documentation describes nested subagents, isolated
non-fork contexts, foreground/background differences, and resumption through an
exact native agent identity. Interactive fork mode can background even non-fork
agents. Sending a message to a completed agent can resume it; user cancellation
must remain distinct from an ordinary partial return. These details motivate
qualification and safe retirement, not a guaranteed native result. Source:
[Claude Code subagents](https://code.claude.com/docs/en/sub-agents).

**Claude model configuration.** Effort and model settings have precedence; a
low-effort environment override is not an isolated coordinator setting. Preserve
explicit engineering selection and inspect actual effective settings. Source:
[Claude Code model configuration](https://code.claude.com/docs/en/model-config).

No new price, benchmark equivalence, provider policy guarantee, model availability,
actual runtime subscription charge or native platform qualification is claimed.
