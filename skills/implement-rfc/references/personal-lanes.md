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
