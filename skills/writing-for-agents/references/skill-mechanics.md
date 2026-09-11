# Skill mechanics

The skill-specific branch of [`writing-for-agents`](../SKILL.md): what changes when the document is a skill (the portable package, the selection that replaces the invocation choice, and splitting). Everything else about writing it is the universal reference in `SKILL.md`.

## Portable package

A shared skill is a plain package, which MASK links unchanged into Claude and Codex at project or personal scope:

- `SKILL.md` frontmatter carries a portable lowercase `name` equal to the package directory and a `description` on one plain or quoted line; multi-line block scalars fail validation. Quote a value containing `: ` or ` #`.
- Supporting files stay inside the package as regular files, conventionally under `references/`, `scripts/`, `assets/` and `tests/`.
- Host activation and invocation controls fail validation: tool grants, hooks, MCP, plugins, `disable-model-invocation`, forked context, and dynamic shell preprocessing. Generated host configuration, such as native role files, is produced outside the package.

`mask skill validate ID --json` reports the exact accepted subset and outranks this summary.

Keep consumer facts out of the package: a consumer's paths, commands and rules live in its `.mask/skill-config/<id>/` context, which the skill reads at run time. Bundled scripts resolve relative to the installed skill; consumer paths resolve relative to the consumer.

## Invocation

Every selected package is model-invoked. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability, and the human can still type the skill's name. Write it model-facing, carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full). A skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place.

The user-invoked half of that choice is not portable here: MASK refuses `disable-model-invocation`, and an invocation `policy` in Codex's optional `agents/openai.yaml` changes one host only, so keep that file to interface metadata. Selection carries the context-load decision instead. Select a skill only where its work happens, through a project declaration for one project's workflow or a personal selection for work done everywhere; a scope that does not select a skill pays nothing for it.

Reach another package by naming its skill, as implement-rfc names attended-review and wizard, never by a path into its directory: install roots differ by host and scope, and the other package may not be selected there. State what the receiving skill needs; a handoff is not an import dependency.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it by name. You pay context load for the new always-loaded description in every scope that selects it, so that independent reach has to be worth it.

Otherwise keep one public skill with plain subordinate references: runtime roles, branch procedures and templates are references or generated configuration, not discoverable skills.

## The human index

With every selected package carrying a description, a **router skill** that only names other skills adds its own context load and removes none. The piled-up cognitive load lives in the catalog instead: the source README's skill table and `mask skill list`. Keep that current, and prune selections rather than adding a skill to remember them.
