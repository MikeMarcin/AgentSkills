---
id: "RFC-DRAFT-0001"
title: "Ledger export"
status: "Proposed"
---

# Ledger export

## Problem and grounded current behavior

The supplied ledger tool writes one CSV from supplied rows, overwriting its destination.
Its `ledger.py` has no batch or resume mode. Operators need bounded exports without
losing existing files or duplicating resumed output. This behavior is proposed; the
fixture code supplies the observed baseline.

## Goals and boundaries

Support local single-file and resumable batch exports. No network upload or deletion.
Each file has at most 100 data rows and a 10 MiB size limit; a job timeout is 30 seconds.
Detailed internal module/class design is deferred; required interfaces are defined.

## Proposed behavior and interfaces

`ledger export OUTPUT` writes a new CSV and refuses an existing destination without
changing it. `ledger batch DIRECTORY` writes numbered files of up to 100 data rows
and records the completed row offset after each file. Resume appends new numbered
files from that offset; it refuses mismatched input identity. An interrupted partial
file is excluded from completed offsets and replaced on resume. A 10 MiB output or
30-second job limit stops with an explicit error and preserves completed files.

## Significant alternatives

Appending to one large CSV simplifies file count but makes interruption recovery
harder to inspect. Bounded separate files were selected for operator recovery.

## Acceptance

- **AC01:** Single-file export refuses an existing destination unchanged, writes CSV
  for a new destination, and stops at the 10 MiB or 30-second limit with an explicit error.
- **AC02:** Batch export partitions data into files with at most 100 data rows, preserving
  completed files when the stated output/job limits stop the operation.
- **AC03:** Resume produces no duplicate data rows, excludes interrupted partial files,
  and refuses mismatched input identity without changing completed files.

## Work and implementation handoff

Proposed cards: DRAFT-0001 (single-file), DRAFT-0002 (batch/resume), DRAFT-0003 (closeout).
Use [the plan](../milestone-plan.json); live import remaps IDs and establishes eligibility.
