# Packet validation results

## Actually executed for this deliverable

**39 payload fixture tests passed.** They include the earlier 19 provider/parser/quota
fixtures plus 20 new project-scope/CLI cases. The new cases exercise nested cwd,
nearest declaration and Git boundary, unavailable and replaced MASK roots, malformed
public envelopes, missing/empty MASK without broader fallback, exact fake-MASK argv,
Windows launcher-template parsing, output preservation, current control target
fields, counter baselines, truncated tails and real temporary Git worktrees.

The full packet was also imported into a **disposable copy of the uploaded
AgentSkills source**, initialized as a temporary Git repository. Its actual canonical
allocator reserved the 21 fixture IDs; a fixture reservation commit preceded live
fixture cards. Its unmodified `scripts/verify_documentation.py` reported:

```text
8 RFCs, 41 cards; 0 structural violations
```

That is the existing four RFCs/twenty cards plus the new four RFCs/twenty-one cards.
The disposable import also passed `git diff --check`. Its temporary SHAs and
reservation are deliberately **not copied into this packet as live provenance**.

The pack validator checks 4 new RFCs, 21 unique cards, 24 criteria, exactly one
closeout per RFC, dependency acyclicity, criterion coverage, internal links,
example safety labels and full file hashes. Supplemental full JSON Schema
validation passed for four schema definitions and 13 example instances in this
build environment. The shipped validator is stdlib-only and does not pretend to
be a general JSON Schema implementation.

## Reproduce the included fixture and packet checks

From the extracted packet directory:

```sh
python3 tools/run_payload_tests.py
python3 tools/validate_pack.py
```

## Not tested or claimed

No live MASK installation, real provider CLI/authentication, native macOS/Windows
process behavior, new runner implementation, billing savings, quota reset or
semantic project improvement was tested here. The Windows test recognizes the
source's exact launcher template; it is not a native Windows run. The existing
private measurement ZIP was not re-collected, modified or bundled.

The runner/adapters, full accounting/reporting layer and live experiments are RFC
implementation tasks. The runnable collector seed still needs production bounded
indexing and source-specific integration checks; its documented gaps remain open
in ASK-0023–ASK-0025. A fixture pass cannot close those acceptance criteria.
