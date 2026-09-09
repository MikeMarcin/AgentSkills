---
schema: "implement-rfc.card.v1"
id: "ASK-0051"
title: "Build the thin coordinator-to-integrator path with explicit engineering authority"
status: "Done"
rfcs: ["RFC-ASK-0010"]
depends_on: ["ASK-0050"]
metadata: {"packet": "agent-skills-interactive-coordinator-2026-09-08", "provisional_id": false, "packet_key": "native-integrator-role-and-routing", "milestone": "M1"}
acceptance: [{"criterion":"AC01-source","outcome":"pass","revision":"2df5aa4bf7e4c863b1f58bff0f6f93c8a42953d9","evidence":{"kind":"observation","detail":"Renderer 19 tests pass after permission inheritance and provider-specific discovery corrections; migration 10 and historical target 1 pass on unchanged relevant inputs. Two linked consumers and single-provider discovery fixtures exercise public renderer. Strong explicit/preserved routes, capability refusal, independent session settings, seven preserved leaf routes, modified-output refusal and rollback covered. Pure native return boundary 5 tests pass, including two generations, correction, duplicate JSON identity, stale mandate and active writers. Canonical source manifest validates. Native host serving remains ASK-0054/0055, not asserted here."}},{"criterion":"AC02-source","outcome":"pass","revision":"2df5aa4bf7e4c863b1f58bff0f6f93c8a42953d9","evidence":{"kind":"observation","detail":"Renderer 19 tests pass after permission inheritance and provider-specific discovery corrections; migration 10 and historical target 1 pass on unchanged relevant inputs. Two linked consumers and single-provider discovery fixtures exercise public renderer. Strong explicit/preserved routes, capability refusal, independent session settings, seven preserved leaf routes, modified-output refusal and rollback covered. Pure native return boundary 5 tests pass, including two generations, correction, duplicate JSON identity, stale mandate and active writers. Canonical source manifest validates. Native host serving remains ASK-0054/0055, not asserted here."}},{"criterion":"AC03-source","outcome":"pass","revision":"2df5aa4bf7e4c863b1f58bff0f6f93c8a42953d9","evidence":{"kind":"observation","detail":"Renderer 19 tests pass after permission inheritance and provider-specific discovery corrections; migration 10 and historical target 1 pass on unchanged relevant inputs. Two linked consumers and single-provider discovery fixtures exercise public renderer. Strong explicit/preserved routes, capability refusal, independent session settings, seven preserved leaf routes, modified-output refusal and rollback covered. Pure native return boundary 5 tests pass, including two generations, correction, duplicate JSON identity, stale mandate and active writers. Canonical source manifest validates. Native host serving remains ASK-0054/0055, not asserted here."}},{"criterion":"AC05-source","outcome":"pass","revision":"2df5aa4bf7e4c863b1f58bff0f6f93c8a42953d9","evidence":{"kind":"observation","detail":"Renderer 19 tests pass after permission inheritance and provider-specific discovery corrections; migration 10 and historical target 1 pass on unchanged relevant inputs. Two linked consumers and single-provider discovery fixtures exercise public renderer. Strong explicit/preserved routes, capability refusal, independent session settings, seven preserved leaf routes, modified-output refusal and rollback covered. Pure native return boundary 5 tests pass, including two generations, correction, duplicate JSON identity, stale mandate and active writers. Canonical source manifest validates. Native host serving remains ASK-0054/0055, not asserted here."}}]
---

# ASK-0051: Build the thin coordinator-to-integrator path with explicit engineering authority

Governing RFC: [RFC-ASK-0010](../../rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md).

## Objective and owned paths

Add the delegating rfc-integrator and independent coordinator/session route without duplicating the old primary. Implement the minimal native dispatch/return path using existing host tools. Preserve selected pre-coordinator engineering routes and every existing leaf route; add the proposed separate integration defaults only for previously unconfigured runs. Version typed delegation policy and any routing extension explicitly. Generated leaf definitions stay non-delegating; the integrator gets only the required role-level delegation. Update historical-target live tests by projecting preserved leaves, not editing retained fixtures. Qualify source behavior now; live driver serving remains ASK-0054/0055.

Owned paths:

- `skills/implement-rfc/config/roles.json`
- `skills/implement-rfc/config/routing.json`
- `skills/implement-rfc/schemas/roles.schema.json`
- `skills/implement-rfc/schemas/routing.schema.json`
- `skills/implement-rfc/scripts/render_runtime_adapters.py`
- `skills/implement-rfc/tests/test_render_runtime_adapters.py`
- `skills/implement-rfc/tests/test_role_migration.py`
- `skills/implement-rfc/tests/test_standard_worker_target.py`
- `minimal entrypoint/handoff wiring coordinated with ASK-0052/0053`

## Acceptance

- Coordinator targets are Sol low / Opus low, with independent integrator resolution and unchanged leaf routes.
- Changing coordinator or scout settings cannot retarget the integrator or other roles; rendered requests bind model and effort together.
- Authority follows the designated integrator on its authorized main/lane scope; an ordinary worker cannot allocate/finish/commit.
- A minimal two-generation fixture distinguishes fresh dispatch from correction resume and keeps integration ownership singular.

Criterion coverage: RFC-ASK-0010-AC01, RFC-ASK-0010-AC02, RFC-ASK-0010-AC03, RFC-ASK-0010-AC05.

## Focused verification

- Focused in-memory renderer and role-migration fixtures; preserved standard-worker routing tests plus new integrator assertions.
- Explicit strong-prior-integrator, missing-route, denied-capability, old-schema and modified-output refusal cases.
- No paid model call or source/deployment mutation is inferred from passing these fixtures.

## Run record

Not started. No native run, source implementation, reservation, accepted work or
measured saving is claimed by this packet. Claim the live card before source work,
preserve unrelated changes and commit only explicit owned paths.
