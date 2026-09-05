# AgentSkills: agent instructions

Read README.md, CONTRIBUTING.md, docs/rfcs/README.md, docs/issues/README.md, the requested live RFC and card, and the nearest nested AGENTS.md. Use the portable implement-rfc workflow with this repository's `.mask/skill-config/implement-rfc/` context. Both canonical skills are deployed through managed links. Verified bootstrap copies are retained outside discovery roots; use README.md for current setup and consumer-context guidance.

This is the private canonical skill library. implement-rfc is imported first; manage-agent-skills second. Program runtime code belongs in ManageAgentSkills.

Routine skill management uses `mask ... --json`, or the known absolute Python entrypoint if PATH is not configured. Inspect capabilities/state and preview meaningful changes. Preserve incremental versus exact-set intent. Never edit MASK's internal state or bypass a collision with destructive shell commands.

Preserve unrelated changes; stage explicit paths. No publication, credential grants, permission changes, unrequested Git push or migration of SRV/SamplePlanner. Test in temporary fixture roots/local bare remotes. No daemon, fleet sync, marketplace, force overwrite or copy fallback. Reorient from live boards and recorded closeouts after interruption.
