# Skill mechanics

Read this when the document is a skill package. It covers package shape,
selection and invocation, reaching other skills, and splitting a skill;
everything else about the writing is in [SKILL.md](../SKILL.md).

## Portable package

A shared skill is a plain package in the source repository. MASK links it
unchanged into Claude and Codex, at project or personal scope.

- `SKILL.md` frontmatter holds a portable lowercase `name` equal to the package
  directory and a `description` on one plain or quoted line; multi-line block
  scalars fail validation. Quote a value that contains `: ` or ` #`.
- Supporting files stay inside the package as regular files, conventionally in
  `references/`, `scripts/`, `assets/` and `tests/`.
- Host activation and invocation controls fail validation: tool grants, hooks,
  MCP, plugins, `disable-model-invocation`, forked context, and dynamic shell
  preprocessing. Generated host configuration, such as native role files, is
  produced outside the package.

`mask skill validate ID --json` reports the exact accepted subset and outranks
this summary.

Keep consumer facts out of the package. A consumer's paths, commands and rules
belong in its `.mask/skill-config/<id>/` context, which the skill reads at run
time. Bundled scripts resolve relative to the installed skill; consumer paths
resolve relative to the consumer.

## Selection and invocation

Treat every selected package as model-invoked. Its description is the outermost
context pointer for the skill, present in every session of each scope that
selects it, and people can still invoke the skill by name. Write the description
for the model; every pointer rule in SKILL.md applies.

No portable field makes a package user-invoked. MASK refuses Claude's
`disable-model-invocation`, and an invocation `policy` in Codex's optional
`agents/openai.yaml` would change one host only, so keep that file to interface
metadata. Control context load through selection instead. Select a skill only
where its work happens: a project declaration for one project's workflow, a
personal selection for work done everywhere. A scope that does not select a
skill pays nothing for it.

## Reaching another skill

Material several skills need can live in one skill that the others name;
implement-rfc reaches attended-review and wizard this way. Name the skill rather
than a path into its directory: install roots differ by host and scope, and the
other package may not be selected there. State what the receiving skill needs; a
handoff is not an import dependency.

## Splitting by invocation

This is the invocation cut; SKILL.md covers the sequence cut. Split off a new
skill only when it has a trigger of its own that people use in prompts, or when
another skill must reach it by name. Each skill adds an always-loaded
description to every scope that selects it, so being separately reachable must
justify that cost.

Otherwise keep one public skill with plain subordinate references. Runtime
roles, branch procedures and templates are references or generated
configuration, not discoverable skills.

## The human index

Cognitive load collects in the catalog: the source README's skill table and
`mask skill list`. A router skill that only names other skills adds its own
description and removes none, because every selected package carries its own.
Keep the catalog current and prune selections instead.
