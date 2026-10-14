# Final public-source preparation evidence

M3 / ASK-0109 and ASK-0110, mandate
`public-prep-final-reconciliation-v1`, coordinator-implementer recipe revision 2.
This records the technical follow-up to [M1 evidence](public-source-preparation-verification.json),
preserving its original scope and observations.

AgentSkills reporting candidate: `c444f558213620230b7bd3c7bdb83970bf2f8f90`.
Accepted M1 input: `8c9c80f05e02e0cbaca56edfde5dab8859f2f932`.
MASK M3 correction input: `ce77dd95c4af947ac4a0c1a73e0e5db9045748ab`, following
accepted M2 input `4ba72a7235d8a94d0d8cb386a672a51e671702bc`.
Each input remains an ancestor of its follow-up candidate.

SECURITY now prohibits sending live credentials through any channel and asks
for sanitized reproduction details through an established private channel.
The [preview page](public-preview.md) describes delivered preparation, preserves
the unanswered license/native boundaries and makes visibility an owner action.
After both repositories become public, the owner manually dispatches both Source
checks workflows on main. Local companion checks, private CI and post-switch
public CI remain separate evidence.

## Focused verification and reused evidence

- Documentation: 15 RFCs, 110 cards, zero structural violations. Portable source
  validates; changed local Markdown links resolve; whitespace check passes.
- Real public MASK examples: two scenarios pass in 23.827 seconds using disposable
  consumers and local bare remotes at AgentSkills `52ea2d9` and MASK `4ba72a7`.
  M3 later changes only reporting/tracker data and one MASK fixture setup; the
  example scripts and production inputs remain unchanged.
- M1's 679 helper cases and 57 other skill cases remain relevant, with two local
  native Windows skips. Its fixture isolation repair retains all assertions;
  corrected complete private CI and final M1 private CI passed, including run
  [38525941795](https://github.com/MikeMarcin/AgentSkills/actions/runs/38525941795).
- M2's 600-case local run found three integration omissions. All were corrected
  and their affected checks passed; the separate added negative-control fixture
  error was corrected and passed. The unchanged evidence is retained, without
  inventing a second all-green full local run.
- MASK private CI [38529937342](https://github.com/MikeMarcin/ManageAgentSkills/actions/runs/38529937342)
  subsequently reported 601 cases, 12 declared skips and four fixture-commit errors.
  Missing consumer Git identity was exposed with strict isolated configuration;
  all seven recovery-entrypoint cases pass at `ce77dd9` in a fresh clone with an
  empty profile and no configured global author. Existing assertions and production
  behavior are unchanged. Final CI observation belongs to the coordinator.

The corrected MASK source subsequently passed full private CI
[38532963256](https://github.com/MikeMarcin/ManageAgentSkills/actions/runs/38532963256)
at `7a97e94`: 601 tests, 12 skips, zero failures. Final metadata candidate
`3f6101d7edafa0da28a71c45c5e1670b764ddcf9` also passed
[38533348436](https://github.com/MikeMarcin/ManageAgentSkills/actions/runs/38533348436):
the same 601 tests, 12 skips and zero failures. The original four errors remain
part of the diagnosis record.

## Intermittent progress-digest correction

AgentSkills CI [38532937786](https://github.com/MikeMarcin/AgentSkills/actions/runs/38532937786)
at `3359319` reported one whole-consumer-tree digest failure in the linked beta
fixture: 679 helper cases, four skips, one failure. Its driver stopped before the
remaining skill suites. Same-input final CI
[38533329416](https://github.com/MikeMarcin/AgentSkills/actions/runs/38533329416)
at `652e528` passed; that intermittent success did not dismiss the failure.

Twenty local Apple Git 2.50.1 courses and twenty pristine Git 2.55.0 courses passed
without a changed path. A disposable upstream Git 2.55.0 build with only a
three-second delay after maintenance detachment then exposed an actual competing
writer. Both alpha and beta snapshots contained Git's empty
`.git/objects/maintenance.lock`; the detached worker removed exactly that file
before the next snapshot. The original whole-tree digest and assertions failed.
No lock was fabricated and no Git path was excluded. The failed CI did not capture
its changed pathname, so attributing that historical failure to this observed
maintenance race is an inference.

Correction `b45c3bbd606a66adc80d22bb0b3be7a839e62d13` disables automatic maintenance
locally in these fixtures before any commit. The shared fixture's optional
parameter preserves its default behavior elsewhere. Production progress/context
helpers, the entire digest function and all three original test bodies remain
unchanged. The same delayed-worker control now passes with no captured lock or
changed byte; the original byte-preservation coverage remains active.

Fresh clone, empty profile, pristine Git 2.55.0 and Python 3.14.7: progress-trail
three cases pass in 1.844 seconds, project-context fifteen pass in 1.940 seconds,
primary-checkpoint two pass in 3.717 seconds. The source manifest was refreshed
with the canonical authoring command; portable source and documentation gates
pass. Exact corrected file hashes and the upstream-source/scheduling-control
identities are retained in private runtime evidence. The temporary diagnostic
build differs from the pristine build and is not installed or deployed. Final
AgentSkills CI for this correction remains a coordinator observation.

No broad unchanged suite, model experiment, real deployment or native qualification
was rerun to close this reporting card. Public companion CI remains a switch-time
step and has not been claimed from private runs.

## Scans, privacy and remaining decisions

Exact reporting/correction candidates were scanned with Gitleaks 8.30.1 default
rules forced through an explicit config, an empty ignore file, ignored allow
comments, full redaction and archive/decoding traversal. Main history, exported
tracked trees and new commit metadata report zero findings. Private runtime records
bind the subsequent final bookkeeping commits, scans and remote main identities.
Unchanged historical blob, ZIP and commit-metadata scans remain prior evidence;
scanner success is bounded evidence, not a proof that every possible secret is absent.

The targeted current cross-platform user-path scan finds only placeholders in
AgentSkills. MASK retains personal path metadata in two immutable provenance files:
`docs/rfcs/assets/mask-corrective-managed-taps.LIVE_IMPORT.md` line 3 and
`docs/rfcs/assets/upgrade-auto-commit/DRAFT_CHECKS.md` lines 9 and 10. These current
tracked bytes are distinct from earlier metadata remaining in Git history and
retained archives. Neither immutable packets nor history were rewritten.

The owner license choice remains unanswered. ASK-0108 and MASK-0140 stay Parked;
no repository-wide license was added. Existing third-party notices and the protected
license/provenance candidate are unchanged. RFC-ASK-0012 native qualification,
RFC-ASK-0014 M4, ASK-0073's visible-run observation and ASK-0102 remain open.
Unavailable native-platform skips do not satisfy those obligations.

The pre-existing AgentSkills lock edit remains excluded, with SHA-256
`65216945daf3d6b0916a9711633aca24833620ba3a7926a3b1972cb09e4a12b9`.
Final ordinary pushes, exact remote revisions, engineering command quiescence and
writer release are recorded in the coordinator's durable M3 handoff. Repository
visibility/access and the existing coordinator-owned license review server remain
separate owner resources.
