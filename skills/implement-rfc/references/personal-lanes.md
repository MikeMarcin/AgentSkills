# Paired personal lanes

Before mutating an active personal lane, validate its pair through
`scripts/personal_lanes.py status --repo-root SOURCE`. Personal tracker `init`
binds the initial checkout. For another source worktree, run `bind --repo-root
SOURCE --tracker-branch TRACKER_BRANCH` to create a tracker worktree from committed
tracker main. Use `--tracker-root TRACKER_WORKTREE` to bind an existing worktree.
Independent clones first require explicit `personal_tracker.py init --workflow-root
TRACKER` association. If another lane owns the supplied tracker checkout, association succeeds
without a lane binding; status remains available, while mutation refuses until
`bind --tracker-branch TRACKER_BRANCH` creates a separate tracker worktree. Source branches are supplied by the contributor; this helper
creates only tracker branches.

The helper returns `portable` repository IDs, branches and revisions separately
from `local` absolute checkout roots. Commit portable records only. Pair records
and synchronization receipts live under `IMPLEMENT_RFC_HOME/runtime`.

A switched or renamed branch refuses mutation. After inspecting both repositories,
use `rebind` with both `--source-branch` and `--tracker-branch`, plus exact current
`--source-revision` and `--tracker-revision`. Rewritten history requires reconciling
acceptance references before `reconcile` acknowledges those same exact revision
arguments. A removed worktree remains unresolved; restore that checkout or
explicitly bind a newly selected worktree. No replacement is guessed.

Reservations require the tracker integrator on main. Lanes inherit committed
reservations when created; integration and reservation commits remain integrator
operations under the shared workflow.

At an authorized synchronization/handoff point, `sync` accepts existing named
`--source-remote` and `--tracker-remote`, exact paired `--source-branch` and
`--tracker-branch`, and `--authorize-push`. Supply that flag only under explicit
push authority. The destinations must differ. Pushes use exact refs without force;
a rejection retains history and a local receipt naming completed sides. Inspect
that receipt and reconcile the rejected repository before retrying. Without remote
arguments, `sync` reports local-only and performs no remote operation. It never
creates remotes or starts background synchronization.

After a rebase, cherry-pick or amended commit replaces recorded source or tracker history,
`reconcile` and `rebind` scan current committed tracker files for references to
retired revisions from each repository, including abbreviations of seven or more hex digits and full SHA-256 revisions.
Replace affected acceptance/continuation references with verified current revisions
and commit the tracker correction before acknowledging the new pair. Historical
tracker commits remain intact. Dirty tracker corrections do not satisfy this gate.

## Release consumed pairs

Use `release --repo-root SOURCE_PRIMARY --pair-record LOCAL_PAIR_JSON
--expected-pair EXPECTED_JSON` after integrating both lane revisions into their
respective main branches. EXPECTED_JSON contains exactly the pair's `portable`
object. The supplied record filename must match the canonical hash of its recorded
source checkout path. First reconcile the pair to the exact integrated lane heads. Release
requires matching repository identities, branches and revisions, clean worktrees
(including ignored files), and no pending product or synchronization receipt.
The archived local record moves outside the active pair registry, freeing the
tracker checkout for another explicit binding. Branches and Git history remain.

Release alone retains existing worktrees. For a consumed secondary worktree owned
by this task, explicitly add `--remove-source --task-owned-source` or
`--remove-tracker --task-owned-tracker`. Only task-owned secondary checkouts can be
removed; primary checkouts remain protected. Git removal uses no force. All
preconditions are checked before removal, and a failed removal retains the active
pair record for inspection and retry.

If a worktree was already removed, select a surviving source checkout in the same
common repository and supply the exact retained pair-record path. Release can
validate the retained branch revision and integration without guessing a new
checkout. Omit removal flags for absent worktrees. Missing/changed branch refs,
unintegrated revisions, dirty worktrees and pending operations remain unresolved.

Release shares the product-operation lock, so active start/finish/recovery operations
refuse concurrent cleanup. If source removal succeeds and tracker removal fails,
the active pair continues to reserve the tracker checkout. Retry release against
the retained record, omitting removal for the now-absent source worktree.
