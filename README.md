# AgentSkills

Private canonical skills for the local MASK workflow. `implement-rfc` was imported first from the supplied packet with its provenance retained; `manage-agent-skills` was added second after the MASK CLI contracts passed verification. The program lives in the separate ManageAgentSkills checkout.

Author each package under `skills/<id>/SKILL.md`. Keep shared instructions portable and project facts in the consumer's `.mask/skill-config/implement-rfc/project.json` and `project.md`. The implement-rfc resolver uses explicit project selection, then its documented environment override, then the consumer Git working directory. Run source-only validation for shared authoring; generating native adapters is a separate explicit consumer operation.

Use a known Python 3.11+ interpreter with `/absolute/path/to/ManageAgentSkills/mask.py capabilities --json` if the MASK launcher is absent. Follow that checkout's README for machine initialization, registration, preview/apply, updates and recovery. Do not edit MASK state files or remove real skill directories to bypass collisions. The management skill is project scoped, not a global installation.

Commit skill payloads, `.mask.json` and workflow context. Generated links, adapters and retained bootstrap backups are ignored individually. Local authoring may deploy a dirty source with a warning; source updates require a clean checkout and affect every registered consumer. Read `docs/rfcs/README.md` and `docs/issues/README.md` for the implementation workflow.

Repository visibility and inherited-source licensing remain unchanged. See `docs/development/skill-provenance.md` and the original packet assets for provenance. Filesystem links do not prove that an already-running agent has loaded the skill.
