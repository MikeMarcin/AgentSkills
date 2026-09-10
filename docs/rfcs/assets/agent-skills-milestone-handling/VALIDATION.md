# Authoring validation — performed checks and limits

The following checks ran against this downloadable packet in the local authoring
container. They establish artifact consistency only. No AgentSkills checkout was
modified, no new production milestone feature was installed, no native model course
ran, and no quota saving is claimed.

| Check | Observed result | Boundary |
|---|---|---|
| `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` | 40 tests passed | Offline plan lint/remapping/rendering, packet integrity and actual local tool stdout/stderr behavior |
| `python3 -B tools/validate_pack.py` | 1 RFC, 7 cards, 2 milestones, 12 acceptance criteria; no errors | Cross-references, dependency consistency, authored group coverage, generated view and file inventory |
| Independent Draft 2020-12 schema validation | Plan schema valid; 4 plan examples passed | Root plan, authoring template, raw fixture plan and partial-plan fixture |
| Uploaded AgentSkills issue schema | 7 proposed cards and 6 raw fixture cards passed | Canonical JSON-valued card frontmatter; no claim of live ID reservation |
| Uploaded `scripts/verify_documentation.py --root <fixture>` | 1 RFC, 7 cards; 0 structural violations | Actual supplied checker in a disposable local Git fixture using the packet's new RFC/cards and snapshot consumer rules |
| Generated `MILESTONES.md` parity | Exact match to canonical plan renderer | JSON is authoritative; readable view is not independently maintained |
| Human/default and explicit JSON invocations | Passed | Ordinary output is readable text; `--json` returns machine data; malformed plans fail |
| Final manifest and ZIP member checks | Passed during packaging | Exact file set, raw-byte hashes, no linked/cache/bytecode payloads, ZIP CRC check |

## What the tests exercised

Positive and negative examples cover omitted defaults, whitespace-stable identity,
retained authored array preference, duplicate JSON keys, input bounds, unsupported
versions, closed fields, empty scope, dependency cycles/self/missing edges, duplicate
milestone IDs, empty/null selectors, whole/partial overlap, disjoint subsets,
required unplanned remainder and unresolved references. Typed ID remapping preserves
milestone identities/prose and refuses collisions; relative criterion remapping is
scoped to its owning source document rather than globally renaming every AC01.

Packet checks also cover card/RFC linkage, acceptance contribution maps, closeout
rows, human-view drift, safe member paths, no mutation during checks and raw fixture
shapes. The test set distinguishes those **40 executed artifact tests** from the
**26 scenario definitions** in `fixtures/scenarios.json`. The latter specify later
implementation/native acceptance; they are not 26 passed production tests.

The supplied documentation checker was run only in a temporary repository with a
synthetic fixture commit and counter. That temporary fixture was removed. Its commit
is not this RFC's real implementation baseline, and no synthetic reservation or
baseline was copied into the packet's live import instructions.

## Still implementation work

The production plan-discovery/adoption helper, installed skill/role behavior,
obligation-bound continuation, safe selected adoption and actual interactive Claude
and Codex courses are not implemented or qualified by these authoring tools. Read
VERIFICATION.md and NATIVE_QUALIFICATION.md at the corresponding implementation
stage. Source schema checks do not prove semantic coverage, milestone sizing, model
judgment, actual host loading, exclusive native ownership or subscription economics.

All RFC and card execution rows remain not run/not recorded. Provisional identifiers
must be reconciled with the live board. The packet's lint/render helper is not a
second production engine and should not be blindly installed as the new workflow.
