# Personal storage

Personal mode keeps the source checkout and the workflow tracker distinct. Use
`scripts/personal_tracker.py --repo-root SOURCE --json init` only after the user
explicitly selects personal mode. Add `--workflow-root TRACKER` to bind an
existing tracker; this also explicitly associates another clone with it. The
command creates no workflow file or Git configuration in SOURCE. It records the
Git common-directory identity under `IMPLEMENT_RFC_HOME` (default
`~/.implement-rfc`) and reports the tracker and runtime roots.

For status, call `scripts/personal_tracker.py --repo-root SOURCE --json status`.
It reads the remembered mode and creates nothing. `--mode project` or
`--mode personal` overrides the remembered selection for that invocation.
`scripts/project_config.py --repo-root SOURCE --json` exposes `source_root`,
`workflow_root`, `runtime_root` and `mode` for subsequent helper calls. An
explicit `--mode personal --workflow-root TRACKER` can inspect an already
configured tracker without a binding, but must agree with one if present; it
never writes a new binding.

For another source worktree, a branch switch or an authorized source/tracker
handoff, follow [Paired personal lanes](personal-lanes.md) before mutation.

Project mode uses the consumer's `.mask/skill-config/implement-rfc/` files as
before. Personal mode reads them from the tracker. The shared board and plan
helpers use the tracker for workflow documents and source checkout for product
evidence. Keep assignments and native return files under the reported runtime
root; they contain machine-local checkout paths. Claim the tracker card before
editing product files. The coordinated product-commit and recovery path remains
pending under RFC-ASK-0013, so do not finish a personal product change with a
standalone source commit.
