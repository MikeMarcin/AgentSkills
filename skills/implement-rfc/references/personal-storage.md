# Personal storage

For explicit first-use setup, select the shared skill at personal scope with
`mask install implement-rfc --user --json`, then preview `mask ensure --user
--check --json`. If role setup is required, use MASK's explicit setup
authorization for that scope; a readiness check never grants it. Personal role
files are rendered from the canonical roles and routes with no project addenda.
A native assignment supplies the selected source root, tracker root, runtime
root, project facts and addenda. Restart a host after role installation and
distinguish its actual loading from MASK's file readiness.

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
Run `scripts/workflow_preflight.py --repo-root SOURCE --mode personal --json`
for the selected source. It checks the bound tracker and MASK's user-scope
native role files without initializing either. Its `host_load` field remains
`not_verified` until a fresh Codex or Claude Code session actually loads and
uses the personal role.

For another source worktree, a branch switch or an authorized source/tracker
handoff, follow [Paired personal lanes](personal-lanes.md) before mutation.

Project mode uses the consumer's `.mask/skill-config/implement-rfc/` files as
before. Personal mode reads them from the tracker. The shared board and plan
helpers use the tracker for workflow documents and source checkout for product
evidence. Keep assignments and native return files under the reported runtime
root; they contain machine-local checkout paths. Before editing product files,
finishing their acceptance, or resuming an interrupted source/tracker commit,
follow [Personal product commits](personal-commit.md). Its committed-claim and
before-edit receipt are required before product changes begin.
