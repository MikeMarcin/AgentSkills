---
id: "RFC-DEMO-0001"
title: "A small persistent name catalog CLI"
status: "Proposed"
---

# A small persistent name catalog CLI

Implement `python catalog.py --store PATH add NAME`, `list`, `rename OLD NEW`, and
`remove NAME`. Store a finite set of nonempty names in the selected file. The first
invocation with an absent file starts from an empty catalog. List prints one name
per line in sorted order. Preserve exact name case in this initial target.

Add rejects an existing exact name; rename rejects an absent source or existing
destination; remove rejects an absent name. A rejected operation returns nonzero
and leaves the existing store unchanged. Malformed store content is a reported error,
not a reason to erase it. Keep the program dependency-free and local; no server,
concurrency protocol, locking service, network, deployment, or paid API is required.

## Acceptance

- **RFC-DEMO-0001-AC01**: Add accepts nonempty names and persists across invocations.
- **RFC-DEMO-0001-AC02**: List prints the exact stored names in sorted order.
- **RFC-DEMO-0001-AC03**: Add/list focused subprocess tests and a runnable example pass;
  duplicate rejection preserves the store.
- **RFC-DEMO-0001-AC04**: Rename changes only the selected existing name; invalid
  source/destination requests preserve the store.
- **RFC-DEMO-0001-AC05**: Remove deletes only the selected name; absent-name rejection
  preserves the store.
- **RFC-DEMO-0001-AC06**: Mutation tests, malformed-store refusal, examples and final
  scoped acceptance pass. No criterion is fabricated or waived by a card heading.
