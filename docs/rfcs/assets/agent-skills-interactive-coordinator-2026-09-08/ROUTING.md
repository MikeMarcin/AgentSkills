# Routing and authority changes

## Owner-selected coordinator defaults

| Driver | Logical session role | Model | Effort |
|---|---|---|---|
| Codex | rfc-coordinator | gpt-5.6-sol | low |
| Claude Code | rfc-coordinator | claude-opus-5 | low |

The coordinator is the existing interactive main session, not another spawned
agent. Rendering a delegated role file does not change that session. Emit small
native session-selection instructions/presets and inspect the requested/effective
selection where the host exposes it. Preserve an explicitly selected different
session; report the difference instead of claiming the defaults ran.

Keep session coordinator settings separate from the `balanced` scout class even
though the initial values match. A later scout or coordinator edit must not alter
the other. Never install a global default that silently lowers every subagent.

## Engineering integrator

Add `rfc-integrator` as a delegating engineering role, with its own integration
route. Resolve it in this order: an explicit integrator choice for this task;
a preserved owner-selected pre-coordinator engineering route; then the separately
stored integration default. Resolve and record it before lowering the main
session's model/effort. After that, the coordinator's current model is never an
implicit integrator choice.

For previously unconfigured runs, this pack proposes initial integration defaults
of **Codex `gpt-6-astra / low`** and **Claude `claude-opus-5 / xhigh`**, copied once
from the supplied standard engineering class into an independent integration
class. This is a new design default, not a measured parity claim or a claim the
owner explicitly selected a new Claude integrator. It keeps the observed Codex
integrator level and does not economize engineering by inheriting Opus/Sol low.
Explicit stronger/different prior integrator settings take precedence. Record
which resolution branch was used. The default is independently adjustable later;
changing `standard` must not subsequently retarget integration.

Bind model and effort together in the actual native role request. A recorded
intent is not enough when a generated file or inherited setting overrides it.
Use supported, guarded per-role rendering/selection for explicit integrator
overrides; preserve existing permissions, speed and all other role outputs.
An unavailable route follows the existing explicit fallback policy, not a silent
model/effort clamp or a coordinator taking over implementation.

## Preserved leaf routes

| Role | Codex | Claude |
|---|---|---|
| rfc-utility, rfc-test-runner | gpt-5.6-luna / xhigh | claude-haiku-4-5 / null |
| rfc-scout | gpt-5.6-sol / low | claude-opus-5 / low |
| rfc-worker | gpt-6-astra / low | claude-opus-5 / xhigh |
| rfc-worker-deep | gpt-6-astra / high | claude-fable-5-1 / high |
| rfc-reviewer | gpt-6-astra / medium | claude-fable-5-1 / medium |
| rfc-reviewer-critical | gpt-6-astra / xhigh | claude-fable-5-1 / high |

These are snapshot configuration facts, not fresh availability or quota claims.
The live source wins if the owner subsequently changed them; record that delta
and preserve their intent instead of downgrading to this snapshot.

## Minimal authoring representation

Use the existing roles/routing source and renderer, not a second model registry.
A versioned schema extension must express:

- the coordinator as a session-only route, independently configurable;
- one delegated `rfc-integrator` with explicit engineering routes;
- an explicit child-role allowlist for that integrator; all existing roles remain
  leaves; coordinator→integrator and integrator→leaf are the ordinary implementation topology; explicit review-only and qualified
  no-grandchildren review relay can dispatch a read-only reviewer from the coordinator;
- optional per-role reference entrypoints, with effective rendered instruction
  identity tracked by the existing source/adapter manifests;
- requested, rendered and actually observed routes/enforcement kept distinct.

The current `may_spawn_utility` boolean cannot express the integrator's authority.
Replace/extend it through an explicit new role schema version, with a narrow v1
reader for owned migration and historical checks. Unknown versions/role selectors
refuse. Do not interpret an ignored new field as enforced nesting. Role allowlists
are policy where the host cannot enforce them; generated leaf tools must still
omit/disable delegation where supported. No arbitrary recursive integrators.

Keep the coordinator out of ordinary delegated role discovery in Codex. A native
Claude main-agent definition may be offered as an explicit launch choice, but
must not force a project-wide default or create an extra spawned coordinator.
Never generate such host activation metadata inside the portable skill payload.

## Permission and runtime caveats

The parent needs the existing permission boundary required for its authorized
children. A behaviorally non-editing coordinator is not a new read-only sandbox
that accidentally prevents the integrator writing. Read-only reviewers retain
their existing actual restrictions. Do not add `acceptEdits`, bypass flags or
approvals merely to make an unattended test pass.

For Claude, check global/model/effort overrides and actual background-tool
availability. `CLAUDE_CODE_EFFORT_LEVEL=low` is not the coordinator preset.
For Codex, check generated-file precedence and whether the integrator has native
agent tools. Only a real launch can qualify nested execution on the selected
host. There is no required API/SDK/programmatic supervisor in either driver.
