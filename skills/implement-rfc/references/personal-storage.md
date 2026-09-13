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

Project mode uses the consumer's `.mask/skill-config/implement-rfc/` files as
before. Personal mode reads them from the tracker. The shared board, claim,
commit and companion helper relocation is still in progress under
RFC-ASK-0013; until it is verified, use setup/status only and keep private
workflow execution pending. Do not write tracker records into the source or
route product commits through the tracker to work around an unsupported helper.
