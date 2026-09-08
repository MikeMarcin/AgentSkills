# Authoring-time packet checks

Performed September 8, 2026 using Python 3.13.5 on Linux.
No Codex/Claude model execution, repository implementation, live ID allocation,
consumer deployment or quota observation was performed.

## Actual results

| Check | Result | Boundary |
|---|---|---|
| tools/validate_pack.py | PASS, zero findings | One RFC, nine provisional cards, fourteen acceptance criteria, 24 workflow cases; paths, links, routing and integrity |
| tools/test_pack.py | PASS, 24 tests, zero skipped on this filesystem | Packet validation and negative mutations; not native scheduling or model behavior |
| JSON Schema Draft 2020-12 check and example validation | PASS using the installed jsonschema validator | Structural return-schema validity and synthetic example only |
| Supplied writing reference retention | Exact bytes copied and hashed | Editorial basis, not empirical model guarantees |

The mutation checks cover corruption/missing/unlisted members, traversal, duplicate
JSON keys, case collision, dangling/cyclic dependencies, incorrect initial status,
missing closeout/criteria, fabricated baseline/acceptance, changed coordinator or
leaf routes, unintended leaf nesting, nonportable skill frontmatter, broken links,
duplicate workflow cases, incomplete implementation coverage, invalid completion
and double-counted fixture totals. The case-collision test explicitly skips on
case-insensitive filesystems instead of overwriting a differently cased file.

All fixture usage values are synthetic. The schema/packet tests do not prove
runtime permissions, host loading, freshness, semantic acceptance or cost savings.
The native qualifications and all RFC implementation acceptance rows remain open.

## Editorial size observations

Counts below use Python str.split() for words and UTF-8 bytes for size. These are
text-size observations, **not model token counts or measured consumption**. Source
sizes identify extracted instruction text, not a full prompt reconstruction.

| Instruction surface | Words | UTF-8 bytes |
|---|---:|---:|
| Supplied SKILL.md | 1,695 | 12,926 |
| Supplied delegated-execution.md | 1,872 | 13,563 |
| Draft coordinator SKILL.md | 682 | 5,197 |
| Draft milestone procedure | 951 | 7,284 |
| Draft handoff reference | 667 | 4,730 |
| Draft delegation reference | 669 | 5,032 |
| Draft verification/closeout reference | 503 | 3,826 |
| Draft attendance reference | 327 | 2,502 |

The draft coordinator plus its dispatch/handoff reference totals 1,349
words before user instructions, native role/tool definitions, selected consumer
rules and results. Those other loads are not zero and were not measured here.
The integrator loads its procedure and relevant references, not the coordinator
loop. The full draft subtree is not meant to be preloaded into any one role.
Verification and handoff rules remain required when their operations occur.

## Reproduce

From the extracted packet root:

```text
python -B tools/validate_pack.py --json
python -B tools/test_pack.py
```

Both shipped commands use only the Python standard library and never run agents
or execute attached repository source. The optional authoring-time jsonschema
check is not a runtime dependency. PACK_MANIFEST.json covers every other delivered
file's exact bytes and SHA-256; it excludes itself to avoid a self-reference.

See VALIDATION.md for future source/native/efficiency acceptance. A valid packet is
ready to import and implement, not proof that the proposed workflow is deployed.
