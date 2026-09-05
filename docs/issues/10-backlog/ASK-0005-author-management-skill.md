---
id: ASK-0005
title: Add the agent-facing MASK management workflow
status: Backlog
rfc: RFC-ASK-0002
depends_on: ["ASK-0004"]
external_depends_on: ["ManageAgentSkills:MASK-0014"]
---

# ASK-0005: Add the agent-facing MASK management workflow

## Objective and owned paths

Own `skills/manage-agent-skills/**`, AgentSkills authoring README and examples.

## Bounded work

Record MASK CLI handoff, write the short safety-first operating procedure, inspect actual capabilities and validate example argv against fixture scenarios. Add this skill only after implement-rfc.

## Acceptance

The second skill manages manifests/registry/update through supported JSON commands, respects scope and never suggests internal-state edits or destructive collision fixes.

## Focused verification

Run `mask skill validate manage-agent-skills --json` against the local candidate source and check examples with fixture CLI; no paid runtime is required.

## Run record

Not started. Record actual commands, outcomes and commits here. Read the live board before claiming. Never stage unrelated paths.
