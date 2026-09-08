# Validation record

This packet specifies an unimplemented follow-up. Checks below were performed in
an isolated local reconstruction of the supplied source; no live repository,
consumer installation, account, model session, or MASK state was changed.

## Performed

| Check | Result | What it establishes |
|---|---|---|
| Existing source `test_render_runtime_adapters.py` | 14 tests passed | Baseline renderer behavior before this RFC |
| Existing source `test_role_usage.py` | 21 tests passed | Baseline audit behavior before this RFC |
| Existing source `test_unified_workflow.py` | 11 tests passed | Baseline shared-workflow behavior before this RFC |
| Packet `test_check_target_routes.py` | 12 tests passed | Exact-target checker detects coupled/old routes and changed limits/leaf boundaries |
| Target checker against unchanged source | Expected nonzero; old names/classes/efforts and CLI floor reported | Prevents calling the current implementation the proposed target |
| Target matrix against current routing schema plus the specified `review` vocabulary extension, in memory | Passed | Proposed configuration structure is coherent; no live schema was modified |
| Supplied repository documentation gate before fixture import | 8 RFCs, 42 cards, 0 structural violations | Reconstructed baseline board consistency |
| Actual allocator used in disposable Git reconstruction, then imported the new RFC/cards and merged index row | ASK-0043–0046 reserved in fixture only | Import mechanics work with supplied allocator |
| Repository documentation gate after fixture import | 9 RFCs, 46 cards, 0 structural violations | New plan fits the canonical board and sole-closeout contract |
| `git diff --check` in import fixture | Passed | No whitespace errors in imported documents |
| Packet validator | Passed | File hashes, one RFC/four cards, dependency graph, six acceptance rows, links and 13 policy cases |

The reconstructed Git commits are fixture identities, not user repository baselines;
they are deliberately not offered as an RFC_BASE_SHA or evidence of live implementation.
Source dump extraction verified section boundaries and recorded source provenance.
No full historical test suite was run or claimed. The recorded optional-station defects
and unrelated work remain outside this small change.

## Reproduce packet checks

From the extracted packet directory, using Python 3.11+:

```sh
python3 -B tools/validate_pack.py
python3 -B -m unittest discover -s tools -p test_check_target_routes.py -q
```

After the RFC is implemented in AgentSkills:

```sh
python3 -B tools/check_target_routes.py --repo-root /absolute/path/to/AgentSkills
```

The last command is supposed to fail against the unchanged uploaded source. It checks
configuration and in-memory native request rendering from the selected trusted renderer;
it does not verify actual model execution, quality, quota use or migration safety.
The implementation cards explicitly require the missing migration/history regressions.

## Not performed

No new worker/reviewer implementation, live adapter migration, native Claude/Codex
serving check, paid request, controlled model comparison, observed saving, MASK
consumer update, or remote fleet rollout. These were not requested as actions during
packet authoring. Required configuration/migration evidence remains future implementation
work; separately authorized runtime/quality observations must not be inferred from
these offline checks. The owner-directed route choice does not require another bakeoff.
