# Writing-for-agents application

The supplied writing-for-agents SKILL.md and SKILL-MECHANICS.md are the editorial
basis. Their heuristics guide the design; they are not empirical promises about
model behavior or substitutes for native qualification.

## Information hierarchy

| Instruction audience | Material loaded for its work | Material reached only by a trigger |
|---|---|---|
| Interactive coordinator | Short SKILL.md, user mandate, selected consumer rules, current dispatch/return | Handoff reference on dispatch/continuation; runtime setup only for missing/incompatible capability |
| Milestone integrator | Its role contract, milestone-integration procedure, current RFC/cards and relevant code | Import/lane, delegation, verification/closeout, attendance and runtime references when those operations occur |
| Worker | Compact role and complete-slice assignment, local applicable instructions, required criteria | Relevant hazards/verification references; not coordinator or pack lifecycle |
| Reviewer | Independent role, acceptance boundary, current candidate and concise evidence | Relevant risk/ownership rules; not implementation conversation |

A file is not free merely because it moved out of SKILL.md. Measure the actual
combined text pulled into each path, including role prompts and mandated consumer
reads. Root/nested instructions still apply even where the host injects them;
this pack does not secretly weaken consumer rules to achieve a word target.

## Editorial decisions

**Ordered steps with completion criteria.** The coordinator has bind, dispatch,
wait and continue/close. The integrator has orient, select a usable milestone,
assign complete slices, implement/check, integrate/accept, hand off. Each phase
has an observable exit condition; finishing a reply is not finishing a milestone.

**Real context boundaries.** New-milestone engineering moves to a fresh child,
not an inline invocation pretending to clear context. Corrections stay with the
current problem. Separating role entrypoints prevents an integrator from spawning
another integrator merely because it reads the top-level coordinator procedure.

**Co-location.** Ownership and stale-result rules live with the handoff;
verification and acceptance live together; attended protection/release lives with
attendance. Avoid re-expanding the same rationale in role JSON, every prompt,
SKILL.md and all references.

**Context pointers.** Pointers name a specific operation and target: Import,
Delegate, Verify, Attend, Resume, Route. A generic “see references” list does not
reliably select the branch. Load a needed mandatory rule before the affected
operation rather than weaken its pointer to improve an apparent prompt size.

**Environment as source of truth.** Read routes, paths, actual commands and board
state from their canonical config/helpers. The runtime draft does not repeat the
model table from ROUTING.md. A renderer may inject short immutable role rules
when that avoids another tool round; report that contribution to prompt size.

**Positive operating instructions.** The coordinator waits; the slice owner
implements and verifies; the integrator adjudicates evidence. Retain explicit
prohibitions only for authority/side-effect boundaries such as no implicit push,
no overlapping writer, no synthetic acceptance and no external supervisor.

**No discovered-skill proliferation.** Keep one public implement-rfc skill and
plain subordinate references. Integrator/leaf role entrypoints are runtime roles,
not a set of new skills that users must remember. Keep a concise portable
`name`/`description`; do not copy host-specific `disable-model-invocation` or
`context: fork` into the plain MASK package. Host-generated configuration belongs
outside the shared payload and remains optional/owned.

## Review gates, not token quotas

Compare entrypoint and per-role common-path word/byte counts to the supplied
source. Use counts to find accidental preload and duplication, not to cut a
required rule or hide a necessary check. Maintain a reachability map for ordinary
implementation, resume, a one-card fix, status-only, attendance, closeout and
runtime-limited execution. A focused tabletop must show the intended next action
from actual rendered instructions, not just the presence of keywords.

No fixed output length, context percentage or per-card reset threshold is added.
A complex milestone can retain more rationale; a simple correction should not
need the whole pack. Keep architectural invariants and unresolved risks in the
handoff even when that makes it longer than the usual few paragraphs.
