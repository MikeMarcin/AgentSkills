---
id: ASK-0001
title: Import supplied implement-rfc as the first skill
status: In Progress
rfc: RFC-ASK-0001
depends_on: []
---

# ASK-0001: Import supplied implement-rfc as the first skill

## Objective and owned paths

Own `skills/implement-rfc/**` and a concise provenance notice. Do not touch SRV or introduce another skill.

## Bounded work

Inventory live AgentSkills. Copy only the packet's clean seed; preserve retained bytes and source attribution. Make the first skill-import commit distinct from adaptation. Keep inherited SRV context inactive outside bootstrap.

## Acceptance

The first skill addition is implement-rfc; all 39 retained hashes match SEED-PROVENANCE.json; caches/resource forks are absent; repository visibility is unchanged.

## Focused verification

Compare retained relative-path SHA-256 values to the packet inventory and inspect the exact Git diff. No live network or runtime delegation required.

## Run record

Not started. Record actual commands, outcomes and commits here. Read the live board before claiming. Never stage unrelated paths.
