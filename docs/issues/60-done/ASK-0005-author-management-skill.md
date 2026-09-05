---
id: ASK-0005
title: Add the agent-facing MASK management workflow
status: Done
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

MASK CLI handoff d8ffdec (runtime f23237d), v0.1.0. Added manage-agent-skills second after initial implement-rfc b7aa506. MASK skill validate and skill-creator quick_validate PASS. scripts/verify_mask_examples.py --mask-program /absolute/ManageAgentSkills PASS on macOS: actual JSON subprocess init/capabilities, add/remove/no-op, stale guard, preserved collision, separate-process intent crash/recover, local bare-remote frozen update, unregister preserving declaration. Structure/diff checks PASS. No private machine paths or engine copied into shared skill. Commit: this Done move.
