---
id: "RFC-ASK-0013"
title: "Optional personal storage for the shared implement-rfc workflow"
status: "Implementing"
---

# RFC-ASK-0013: Optional personal storage for implement-rfc

Accepted user mandate: `/tmp/implement-rfc-personal-2026-09-13/mandate.md`, revision 1, run `personal-mode-20260913`. The [authored plan](plans/personal-implement-rfc/milestone-plan.json) governs integration. [ASK-0082](../issues/10-backlog/ASK-0082-close-personal-implement-rfc.md) holds the immutable baseline, criterion results, and current frontier.

## Decision and authority

Keep one implement-rfc skill and one shared planning, board, coordinator, integrator, acceptance and recovery procedure. Project mode remains valid. Explicit personal selection binds one entire Git common repository to one external tracker Git repository; subsequent invocation uses the machine-local binding unless an explicit mode overrides it. A missing binding never silently changes modes. `IMPLEMENT_RFC_HOME` defaults to `~/.implement-rfc`. Local bindings, process identities, locks, logs and sessions stay outside both repositories. Portable RFCs, cards, plans, reservations, evidence and continuation records commit to the tracker.

The private boundary covers workflow-generated project files, Git metadata, commit messages, branch names and publication text. It does not promise invisibility to local inspectors or providers and does not override actual contributor requirements. Product commits contain only selected source changes and ordinary messages. No source-worktree setup file, exclusion, hook, config, ref or link is installed by personal setup. Observational commands do not bootstrap. No push, publication, credentials, persistent permission change, or unrelated consumer migration is authorized by this RFC.

## Shared context and storage

The resolver distinguishes source checkout, workflow repository/worktree, runtime location and mode. `--repo-root` remains the source checkout; `--mode project|personal` and `--workflow-root` control selection explicitly. Project mode's existing context is unchanged. Personal mode resolves workflow documents from the tracker; source inspection, tests, baseline and product commits use the source. It rejects overlapping repositories and unsafe redirection. One Git common repository shares one binding across its worktrees. Another clone requires explicit association, never remote-URL guessing. A supplied tracker may live outside `IMPLEMENT_RFC_HOME`; a managed local tracker is created there.

Each active source lane pairs with a tracker branch and worktree. Assignments and handoffs carry both repository identities, roots, branches and revisions. The tracker integrator allocates IDs and commits reservations on tracker main. Branch switches, renames, removed worktrees and mismatches stop mutation until reconciled. Separate source and tracker commits are linked by a durable external operation receipt. A failed half-operation preserves its successful effects and resumes without reset, duplicate product commit or false completion. Rebase/cherry-pick requires revision-reference reconciliation. Authorized synchronization follows existing branch/handoff rules; local-only trackers do not acquire remotes or background sync. Cleanup touches only consumed task-owned worktrees.

## Native and companion integration

Install the canonical skill and generic roles at personal scope. Render personal roles from the same definitions and route table; assignment supplies project facts/addenda. Distinguish files from observed host loading. MASK owns scope-specific readiness for personal roles and source/tracker binding, while project readiness retains consumer inputs. Attended-review and wizard accept explicit external runtime state while protecting source candidates and executing in the source root. Remote handoffs carry both roots and revisions or refuse before project-local metadata writes. Existing active runs and consumers adopt only at safe boundaries.

## Acceptance criteria

- **RFC-ASK-0013-AC01 — Explicit selection and identity.** Explicit personal setup creates or binds a managed/supplied tracker, remembers mode per Git common repository, shares it across worktrees, requires explicit clone association, and never silently switches modes.
- **RFC-ASK-0013-AC02 — Context and footprint.** Shared public helpers distinguish source/workflow/runtime roots; project mode remains compatible; setup and observation leave source checkout and Git directory untouched; unsafe overlap/redirection is refused.
- **RFC-ASK-0013-AC03 — Full workflow path.** Public helpers complete initialization, plan intake, claim, implementation, verification, source commit, interruption, resume and closeout with portable tracker records and machine-local runtime data.
- **RFC-ASK-0013-AC04 — Paired lanes.** Concurrent paired worktrees, reservations, lane integration and mismatched/removed/renamed/switching source state reconcile without guessed replacement lanes.
- **RFC-ASK-0013-AC05 — Product privacy.** All generated source commits, messages, branch names and proposed publication text are free of private IDs, paths and bookkeeping; explicit-path source commits preserve unrelated edits.
- **RFC-ASK-0013-AC06 — Recoverable dual commits.** Failure before/after source/tracker commits retains truthful receipts, preserves successful effects and unrelated work, avoids duplicate commits, and refuses ambiguous recovery.
- **RFC-ASK-0013-AC07 — Synchronization.** Local bare-remote tests prove separate destinations, authorized corresponding handoffs, branch restrictions, local-only operation and conflict preservation; no implicit push.
- **RFC-ASK-0013-AC08 — Parity.** Shared planning, partial acceptance, stale-return rejection, human-pending and closeout scenarios work in both modes through the common procedure.
- **RFC-ASK-0013-AC09 — Personal native roles.** Canonical routing renders personal roles and selected preflight reports readiness separately from actual loading; both Codex and Claude Code load and perform a bounded source/external-state course before native support is accepted.
- **RFC-ASK-0013-AC10 — Companion and remote state.** Attended-review, wizard and compatible remote handoffs use explicit external state with source-root candidate protection; incompatible adapters refuse before source-local metadata writes.
- **RFC-ASK-0013-AC11 — Instruction quality.** One skill keeps common obligations authoritative; personal-only guidance is conditionally loaded. Fresh-agent tabletop checks cover first use, resume, small fix, status-only and paired worktrees in both modes.
- **RFC-ASK-0013-AC12 — Bounded adoption and closeout.** MASK handoff is recorded at actual revisions; selected personal deployment is reviewed at a safe boundary; every criterion links direct evidence and unresolved native/human checks remain open.

The accepted mandate's detailed behavior and test cases remain binding when a card abbreviates them. This RFC does not supersede RFC-ASK-0012 or reopen its parked native acceptance.
