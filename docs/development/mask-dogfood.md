# Named MASK dogfood — 2026-09-05

The authorized integration registered only AgentSkills and ManageAgentSkills in the local MASK machine registry. Both portable manifests now require `implement-rfc` and `manage-agent-skills`, targeting Claude and Codex. MASK created all eight directory links from guarded prospective membership plans; no hand-written deployment links were used.

AgentSkills' 39-file real bootstrap copy matched the supplied seed plus exactly `config/project.json` and `references/project.md` overrides. Inventory digest: `cfeaf6a03e638c502724a686bb37a7f127e7da1f1bf7520962ed2903468b2043` (SHA-256 of the sorted per-file SHA-256 map). It was untracked and contained no links. The independent known-good copy is retained at `.mask/bootstrap-retired/implement-rfc-2026-09-05`, outside discovery roots. No Claude shim or native adapters existed to retire. Modified/unrecognized content was not encountered.

Actual shared-link invocation of `scripts/audit_board.py` passed in both consumers. `resolve_context()` selected `agent-skills` here and `mask` in ManageAgentSkills while returning the same canonical asset root. The shared SKILL.md and source payload stayed unchanged through cutover. Host UI skill discovery/loading was not observed; these are filesystem and bounded script-invocation results.

The management example scenario now lives canonically in ManageAgentSkills `tests/test_end_to_end.py`; `scripts/verify_mask_examples.py --mask-program PATH` invokes that exact public-CLI fixture. The fixture covers JSON/exit status, guard/refusal preservation, crash recovery, frozen local-remote update, no-op and unregister. This avoids maintaining two copies of the scenario.

Handoffs: first shared skill closeout b66a562; provenance location correction ed19f5e; management skill 11d43f5 and closeout d8edaa8; MASK update/install handoff d8ffdec. MASK-0015 records the resulting AgentSkills manifest integration commit.
