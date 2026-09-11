---
schema: "implement-rfc.card.v1"
id: "ASK-0068"
title: "Give attended verdicts an engineering owner and survive hosts without SendMessage"
status: "Done"
rfcs: []
depends_on: []
priority: "P1"
metadata: {"origin": "SampleReview UX redesign coordinator session, 2026-09-10", "skills": ["implement-rfc"]}
acceptance: [{"criterion":"coordinator-forwards-pointers-not-conclusions","outcome":"pass","revision":"d435015e53b39d395c399b77a2df933161a8b742","evidence":{"kind":"command","detail":"test_verdicts_go_to_the_integrator_and_resume_has_a_fallback asserts SKILL.md step 4 forbids summarising or interpreting the note and attendance.md names the forwarded session id, cursor and candidate ids."}},{"criterion":"no-sendmessage-dispositions-and-quiescence","outcome":"pass","revision":"d435015e53b39d395c399b77a2df933161a8b742","evidence":{"kind":"command","detail":"coordination-handoff.md gains 'Hosts without SendMessage' with the fresh-dispatch path, fresh-dispatch-ready returns and the quiescence check; both disposition rows name the fallback; the test guards each."}},{"criterion":"desktop-code-tab-observation-recorded","outcome":"pass","revision":"d435015e53b39d395c399b77a2df933161a8b742","evidence":{"kind":"observation","detail":"runtime-compatibility.md records the 2026-09-10 desktop app Code tab observation on Claude Code 2.1.260 as dated, separate from terminal CLI behaviour, linking the handoff section."}},{"criterion":"routes-addenda-allowlists-byte-identical","outcome":"pass","revision":"d435015e53b39d395c399b77a2df933161a8b742","evidence":{"kind":"command","detail":"git diff of config/, schemas/ and generated/ excluding the regenerated manifest is empty; validate_portable_agents --source-only valid and --compare SamplePlanner identical; 19 renderer tests pass."}}]
---

# ASK-0068: Give attended verdicts an engineering owner and survive hosts without SendMessage

## Problem

On 2026-09-10 a coordinator session (claude-opus-5, effort low, Claude desktop app Code tab) received the human's rejection of SRV-0646, read the note itself, decided that one symptom made four other candidates unjudgeable, and ruled that a remark about the Home flow was a requirement change rather than a defect. That is verdict interpretation and scope adjudication, which `references/attendance.md` already assigns to the engineering integrator. The coordinator did it anyway because step 4 of SKILL.md hands the return to the coordinator and nothing says "forward the session pointer unread".

It could not resume the integrator either: the host reported `SendMessage is disabled for this session, in subagents as well as here`. The skill's continue-milestone disposition assumes resume exists. The coordinator then dispatched a fresh integrator with a hand-written summary, and two earlier children of the retired integrator were orphaned.

## Objective and owned paths

Owned surfaces: `skills/implement-rfc/SKILL.md` steps 3 and 4, `references/attendance.md`, `references/coordination-handoff.md`, `references/runtime-compatibility.md`, `scripts/workflow_preflight.py` if it gains a host-capability field, and the instruction tests under `skills/implement-rfc/tests/`.

## Bounded work

- Verdict intake: the coordinator forwards the attended session id, the `status --after` cursor and the exact candidate ids to the integrator as the milestone objective. It does not summarise, rank, or interpret the human's note, and it does not decide which other candidates a rejection invalidates. Interpreting a rejection to a root cause is a named unresolved reasoning problem the integrator may delegate to `rfc-worker-deep`; the integrator route itself is unchanged unless the owner decides otherwise.
- Resume fallback: at bind time the coordinator records whether the host exposes `SendMessage`. Where it does not, `continue-milestone` and `review-request` resolve to a fresh `rfc-integrator` dispatch carrying the previous return's continuation pointers and a renewed dispatch identity; the integrator's compact return must already be fresh-dispatch-ready. Before retiring an integrator on such a host, the coordinator confirms its children are quiescent, because nothing can reach them afterwards. Record in `runtime-compatibility.md` that the Claude desktop app Code tab (2.1.260) lacks `SendMessage` in the interactive session and that the terminal CLI is the qualified host for resume.
- Keep the existing rule that the coordinator never substitutes its own route for engineering; add the explicit failure this run showed: a low-effort coordinator with the verdict in hand is not authorised to adjudicate it.
- Instruction tests cover the forwarded-pointer contract and the no-SendMessage disposition table.

## Acceptance

- After a hand-back, the coordinator's next dispatch or resume carries only session id, cursor and candidate ids plus the unchanged mandate; a test over the rendered coordinator instructions asserts the prohibition on interpreting the note.
- On a host without `SendMessage`, the disposition table names the fresh-dispatch path and the quiescence check, and the rendered `rfc-integrator` return contract requires fresh-dispatch-ready pointers.
- `runtime-compatibility.md` records the desktop Code tab observation with date and version, separated from terminal CLI behaviour.
- Existing routes, addenda and role allowlists are byte-identical after the change; `validate_portable_agents.py --compare` still passes for both consumers.

## Verification and execution record

Source revision d435015e53b39d395c399b77a2df933161a8b742. Instruction-path tests: 4 pass, including the new guard over the forwarded-pointer rule, the no-SendMessage disposition rows and the dated desktop observation. Renderer tests: 19 pass. Full implement-rfc discovery: 461 tests, 8 skipped, 1 failure that is pre-existing at HEAD (`test_standard_worker_target` expects the Claude integration route opus/xhigh; commit 0af7c0e set it to fable/low without updating the test). Documentation gate: 12 RFCs, 68 cards, 0 violations. `validate_portable_agents.py --source-only`: portable source valid after regenerating the manifest; `--compare` against SamplePlanner's installed skill: identical. `config/`, `schemas/` and rendered role text are byte-identical to the pre-change head; the fresh-dispatch-ready return requirement lives in the compact-return contract of coordination-handoff.md, which the rendered integrator role already binds through its entrypoint, rather than in roles.json. `workflow_preflight.py` was not changed; the SendMessage record is a coordinator bind-time observation.

Pre-existing consumer drift, outside this card: `validate_portable_agents.py --repo-root SampleReview` reports its `.claude/agents/rfc-integrator.md` as stale or unrecognized at the head before this card's commits; reconcile through MASK in that consumer.
