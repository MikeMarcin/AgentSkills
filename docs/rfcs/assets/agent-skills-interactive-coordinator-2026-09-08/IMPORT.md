# Import into the live AgentSkills board

## Source boundary

The supplied AgentSkills dump was generated on September 8, 2026 at 08:49:51 PDT.
It contains RFC-ASK-0001–0009 and NEXT_ID `ASK-0050`. This packet proposes
RFC-ASK-0010 and ASK-0050–0058. No live ID or commit has been reserved here.

Import on the integration branch selected by current consumer rules (the supplied
AgentSkills context says `main`). The existing main integrator imports while the
new role does not yet exist; installing this design is not permission to bypass
that bootstrap authority rule.

## Procedure

1. Validate this packet with `python -B tools/validate_pack.py`. Read root/nearest
   instructions, the two consumer-context files, RFC and issue indexes. Inspect
   Git root, branch, status, current allocator history and pending assignments.
   Preserve unrelated changes; resolve an occupied index without sweeping it.
2. Reconcile the proposed RFC and card IDs against the live board. Reserve nine
   issue IDs through the repository's existing public allocator, such as
   `python scripts/allocate_issue_id.py --count 9 --reserve-for coordinator-milestones`.
   Use the live allocator's returned paths and IDs, not hand-edited NEXT_ID.
   Commit its counter and receipt before using the reservation. Never recycle IDs.
3. Capture the actual pre-implementation Git revision as RFC_BASE_SHA on the new
   closeout. The dump timestamp, pack checksum and prior reuse-patch commit are
   provenance, not substitutes for that baseline. Source changes cannot precede
   this anchor. Record original IDs and live IDs in LIVE_IMPORT.
4. Copy only the new live RFC and nine cards into the configured tracker paths.
   Reconcile filenames, frontmatter, links, dependency IDs and acceptance IDs
   together if renumbering is needed. Import the RFC as Proposed, then record the
   owner's implementation direction as acceptance through the normal lifecycle.
   Exactly the intake card is initially Ready; all dependent cards are Backlog.
5. Retain this complete packet under
   `docs/rfcs/assets/agent-skills-interactive-coordinator-2026-09-08/`, outside the
   live card/RFC index. Add the adjacent LIVE_IMPORT mapping and a new RFC index
   row. Do not overwrite either tracker README or install `draft/` as source.
   Do not copy this order document as another mutable tracker.
6. Commit explicit import paths and run
   `python -B scripts/verify_documentation.py --root .` plus the installed helper's
   scoped queue/validation. Use current flags from its --help. Finish intake only
   after live linkage, one closeout, dependency status and baseline are correct.

## Preserve settled history

This is a prospective follow-up to RFC-ASK-0003/0005/0007/0008/0009. Preserve their
RFC bodies and historical closeouts, including ASK-0048/0049 and the inconclusive
older efficiency experiments. Update active documentation and tests where this
RFC changes current policy. Tests that require exactly the historical seven-role
set must preserve those seven routes while allowing the new integrator; do not
edit the retained historical target fixture to pretend it originally had eight.

The supplied reuse patch is already in the supplied current source. Keep its
same-problem corrections/fresh unrelated work rules. The earlier audited run
predated that patch; do not reverse the current source for implementation.

## LIVE_IMPORT minimum

Record packet ID/hash, original→live RFC and card mapping, actual baseline,
import commit when known, live destinations, retained packet location, source
changes since the dump, explicit deployment scope and unperformed native checks.
Actual revision fields remain UNRECORDED until observed. The implementation plan
never supplies fabricated reservations, approvals, completed cards or evidence.
