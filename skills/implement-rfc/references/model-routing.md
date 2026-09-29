# Model Routing And Updates

`config/routing.json` v2 owns independently stored coordinator session routes and
delegated engineering routes. Rendering never changes the active session.
The coordinator is not a delegated role. Bind the integrator first: explicit task
choice, preserved owner engineering choice, then independent integration default.
The coordinator's current route is never an implicit engineering override.

| Role | Class | Codex | Claude |
|---|---|---|---|
| `rfc-utility`, `rfc-test-runner` | mechanical | Luna xhigh | Haiku 4.5 unsupported/null |
| `rfc-scout` | balanced | Sol low | Opus 5 low |
| `rfc-worker` | standard | Astra low | Opus 5 xhigh |
| `rfc-implementer` | implementation | Sol 6.1 xhigh | Opus 5.5 high |
| `rfc-integrator` | integration | Sol xhigh | Opus 5 xhigh |
| `rfc-worker-deep` | deep | Astra high | Fable 5.1 high |
| `rfc-reviewer` | review | Astra medium | Fable 5.1 medium |
| `rfc-reviewer-critical` | critical | Astra xhigh | Fable 5.1 xhigh |

Standard is broad engineering; deep addresses named unresolved difficulty.
Review is independently configurable from deep implementation. Critical review
addresses a named material risk and replaces normal review when selected; no
medium-then-critical pipeline. Effort does not change acceptance or authority.
See [delegated execution](delegated-execution.md) for selection and contracts.

This is the owner's 2026-09-08 allocation decision, with the integrator moved to Sol
xhigh / Opus 5 xhigh on 2026-09-11 and the Claude implementer moved to Opus 5.5
xhigh on 2026-09-22, the Codex implementer moved to Astra xhigh on
2026-09-25, and the Claude implementer moved to Opus 5.5 high on 2026-09-28, and the Codex implementer moved to Sol 6.1 xhigh on
2026-09-29, not measured quality equivalence or subscription
savings. No live bakeoff is required for this promotion. Exact
model IDs and requested effort live in configuration; requests do not prove serving.
Claude's declared floor is 2.1.255; no automatic client upgrade, effort clamp,
model fallback, reset or credit purchase is authorized. Preserve processing speed.

## Native dispatch arguments

A generated custom role already binds its model and effort. Omit optional
per-call overrides when spawning it. For Claude `Agent`, choose the custom role
without adding `model: sonnet`, `opus` or another family alias. If an actual host
requires explicit model/effort fields, preserve the authorized exact pair and
verified capability; inability to express it is a capability gap, not permission
to substitute. Keep actual call arguments distinct from configuration, banners
and serving telemetry. A conflicting launch request fails route qualification
until corrected and rechecked through that native boundary.

## Lane Runtime Selection

Each class has both a Codex and a Claude route. In a Claude Code primary
session, native Claude agents are the default lane mechanism;
`scripts/codex_lane.py` selects the same canonical role's Codex route instead
(read [codex-lanes.md](codex-lanes.md) first). Choose per lane:

- Use one independent reviewer when useful, preferring the opposite model family
  from the implementation when the driver can launch it. Different families can
  add diversity; that is not a guarantee of independent errors.
- Use the critical role instead of the ordinary reviewer for a named material
  risk. A second review, including another provider running the same role,
  requires an unresolved material concern or an explicit request. Reconcile
  findings using direct evidence, not a vote.
- Prefer Codex for mechanical bulk when allowance economics favor it.
- The designated integrator never runs through the launcher; it launches lanes only.

A driver unable to launch the other family uses its native reviewer and records
that limitation. Record each review's runtime per [codex-lanes.md](codex-lanes.md).
If the runtime exposes a fallback model or effort, report its effective value
in the startup banner. Bedrock availability remains environment-specific; confirm
approved inference profiles before relying on those routes there.

## Mechanical Work Boundaries

Utility handles read-only mechanical work. The test runner can also write
assigned disposable build/test outputs, but has no acceptance authority.
Neither chooses architecture, implementation strategy, root cause, or
verification sufficiency. Run trivial deterministic commands directly rather
than spawning an agent. Workers normally run their own focused checks; a
separate test runner is optional when it materially helps execution.

Send failure diagnosis to a scout. Send questions about whether tests can pass
while an RFC claim remains false to a reviewer or the integrator. The integrator
selects sufficient verification and adjudicates all acceptance decisions.

## Critical Review Selection

Consider `rfc-reviewer-critical` when the user requests independent critical
review or the final diff materially affects one or more of:

- wire or protocol contracts;
- persistence or migration behavior;
- authority or security boundaries;
- concurrency primitives;
- destructive migrations.

Selection remains discretionary: use review only when it is likely to add
discriminating evidence. For other work, a integrator skeptical pass is
sufficient. A reviewer may block only on an evidence-backed failure of an
existing acceptance criterion or a critical regression in the changed surface.

## Claude Through Bedrock

The generated Claude agents always name stable Anthropic model IDs. Keep those same definitions at home and work. On Amazon Bedrock, map the IDs to approved inference-profile ARNs with Claude Code's native `modelOverrides` setting.

1. Open `config/claude-bedrock-model-overrides.example.json`.
2. Replace each example ARN with the approved organization inference profile.
3. Merge the `modelOverrides` object into the applicable Claude Code settings source:
   - organization-managed settings when the mapping is centrally governed;
   - `.claude/settings.local.json` for a developer-local mapping when policy permits it.
4. Keep account IDs and private deployment ARNs out of the portable skill and generated agent files.

`modelOverrides` lets Claude Code retain the canonical model family and capability identity while sending the provider-specific ARN to Bedrock. When managed `availableModels` policy is active, the organization may need to own the overrides because lower-precedence mappings can be ignored.

Unverified as of 2026-08-02: the `modelOverrides` setting could not be confirmed in official Claude Code documentation. Before relying on role-to-model routing through Bedrock, verify on the Bedrock-configured machine that each generated agent's startup banner reports the expected model; if the setting is ignored, route through organization-managed model policy instead.

Do not set `CLAUDE_CODE_SUBAGENT_MODEL` when role-specific routing is expected. That environment variable overrides every subagent definition's model.

## Rendering And Candidate Evaluation

Rendering injects each selected role, model, and effort into that native agent's mandatory first-line startup banner. A route with no supported effort renders as `none (unsupported)`. Regenerate the adapters whenever a route changes so the banner cannot drift from the native model configuration.

Render the checked-in assignments:

```sh
python .agents/skills/implement-rfc/scripts/render_runtime_adapters.py
```

For a candidate model mapping, create a small JSON overlay and render into a temporary repository root so the checked-in adapters remain untouched:

```sh
python .agents/skills/implement-rfc/scripts/render_runtime_adapters.py \
  --repo-root /tmp/implement-rfc-candidate \
  --routing-override /tmp/routing-candidate.json
```

## Updating Models

When a new model or effort level appears:

1. Add it to a candidate overlay or a branch of `config/routing.json`.
2. Render the native adapters into a temporary root.
3. Run the deterministic adapter tests and drift check.
4. Evaluate the candidate on representative historical RFC work:
   - exact locating, command execution, and log condensation for the mechanical lane;
   - ownership and execution-path discovery;
   - build/provider selection analysis;
   - bounded implementation with direct tests;
   - independent review of known overclaim or missing-verification cases.
5. Compare accepted findings, false positives, rework, elapsed time, and token cost against the incumbent.
6. Promote through `config/routing.json`; update role contracts and schemas too when responsibilities or classes change. Update `verified_as_of`, render, validate, and commit the source and generated outputs together.
7. Retain the previous routing revision in version control for immediate rollback.

Absent an explicit owner-directed promotion, establish a newly released model on representative utility, scout, or shadow-review work before assigning implementation or closeout-critical responsibility. An owner-directed promotion can proceed on documented public evidence and judgment; state which local evaluations were not performed.


For owned adapter retirement, active sessions, pins and rollback, use [scoped adoption](role-adoption.md).

## Coordinator and integrator selection

The public renderer accepts `--integrator-route FILE` and
`--preserved-integrator-route FILE`, each a JSON object mapping provider to an
exact `{"model":"...","effort":"..."}` pair. Pass `--capabilities FILE` with
verified provider/model supported efforts for overrides. Explicit task choices
win preserved engineering choices; defaults are independently configured in
`integration`, not copied from the current coordinator or scout at run time.
Preserve these exact inputs for check/resume and inspect route origins on the
owned adapter manifest. Unknown or unsupported choices refuse; no silent clamp.

Coordinator defaults are `session_routes.rfc-coordinator`; use the native host's
session controls only after binding engineering. Preserve an explicit owner
session choice and report a difference from the defaults. Do not set a global
subagent model or a global low-effort environment variable. The renderer records
session-selection instructions and requested routes without applying them.

For source authors, run `scripts/render_runtime_adapters.py --write-source-manifest`
from the canonical checkout after changes, then
`scripts/validate_portable_agents.py --source-only`. For an explicitly selected
consumer, render with `--repo-root ROOT`, inspect the owned result and use the
same options with `--check`. Preserve active assignments and ownership markers;
never write through shared skill links or overwrite unexpected generated content.
Roles/routing v2 express typed delegation; the narrow v1 reader admits historical
leaf definitions without inventing delegation authority. Unknown versions refuse.
