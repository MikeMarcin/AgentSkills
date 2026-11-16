# RFC-ASK-0019 verification

Source candidate: `670238c425c0e2fcaa4475df9a1368c0eaac0f14` (AgentSkills `main`). RFC_BASE_SHA:
`5fd9ad3951934469593be781e6078927c9e20c23`. Strategy: coordinator-implementer,
one milestone `checked-question-format` (ASK-0134, closeout ASK-0135). No human
attended review is required by the RFC and none was held. Source-only: no consumer
was migrated, no skill deployed, and no BetterPullReview or aito state was changed.

Focused commands, run against the candidate:

- `python -B -m unittest discover -s skills/attended-review/tests -v`: 62 tests OK
  (53 existing, 9 new in `tests/test_question_format.py`).
- `node skills/attended-review/tests/review_page.test.js`: PASS (existing page behavior).
- `node skills/attended-review/tests/review_page.test.js --parts SNAPSHOT`: PASS, run by
  `test_each_kind_is_admitted_and_its_parts_render_in_order_live_and_offline` on the
  real helper's `status --full` of the portable example.
- `python docs/rfcs/plans/attended-review-question-quality/ac07_differential.py --repo-root .`:
  `"pass": true` ([output](ac07-differential.json)).
- `python scripts/verify_documentation.py --root .`: 0 structural violations.
- `python skills/implement-rfc/scripts/validate_portable_agents.py --source-only`: valid.
- Two disposable consumers, each with `.agents/skills/attended-review` symlinked to the
  source, ran `check` (failing manifest, exit 1), `init` and `prepare` of
  `examples/question_kinds.py` output: separate sessions, builds waiting for a launch
  check, design/decision/audio ready.
- Headless Chrome rendered the offline HTML ([screenshot](browser-offline-build.png))
  and the live loopback page of one fixture consumer ([screenshot](browser-live-build.png));
  the host was stopped afterwards. Fixture images are flat placeholders.

| Criterion | Check / command | Outcome | Revision |
|---|---|---|---|
| AC01 | `test_each_kind_is_admitted_and_its_parts_render_in_order_live_and_offline`; page `--parts`: the page's part order matches the defined order, no identity line exists above the title, candidate ID and revision appear only in provenance, and live and offline pages render identical parts for every question; browser screenshots of both | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC02 | page `--parts`: one Copy click puts the launch command, and one puts the step value, on the clipboard; Reference and Now figures sit in one comparison grid, captioned `Reference: …` and `Now: …`; screenshots show them side by side | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC03 | `test_a_build_question_waits_for_its_launch_check`: static `prepare` leaves the build waiting, unprotected, with the launch-check reason and no repeated event; a passing `prepare` command makes it ready, a failing one leaves it waiting; `ready --evidence` makes it ready and protected; a version-2 launch question is still made ready statically | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC04 | `test_a_manifest_breaking_several_rules_is_refused_whole_and_check_reports_the_same`: 16 violations across two questions named at once with rule ID, part and fix; no session created; an existing session's bytes unchanged; `check` exits 1 with the identical violation list and touches nothing; `check` needs no session | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC05 | `test_a_waiver_admits_the_question_shows_its_reason_and_binds_the_fingerprint`: unwaived question refused, waived one admitted and counted (`waivers: 1`), reason embedded in the page and shown in the Exceptions part (page `--parts`), rewording the reason changes the fingerprint; empty, unknown and unwaivable waivers refused; a 26-word reason breaks `waiver-reason-words` | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC06 | `test_shared_setup_is_stated_once_and_every_question_keeps_its_launch` and page `--parts`: both group questions store the setup note and launch; the note shows on entering the group, not on moving within it, and again on re-entering; each question copies its launch; the note binds the group's fingerprints only; a 41-word note breaks `setup-note-words` | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC07 | `ac07_differential.py` against the RFC_BASE_SHA helper: for version 1 and 2 manifests that break the rules, fingerprints, every command output except init's added `checks`, and normalized session state are identical through init, prepare, import, re-import, hand-back and status; `test_legacy_manifests_are_admitted_with_violations_reported` checks golden fingerprints captured from 5fd9ad3 and the `unchecked legacy format` report; the existing golden v1 fingerprint and all 53 earlier tests pass | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC08 | `test_the_guide_example_passes_within_eighty_words`: the guide's after-example, a rewrite of BetterPullReview `BPR-2032-import-preview-b` (decided 2026-11-16T03:07:58Z, the latest decided question found in that project's stored sessions), passes `check` with 75 driver-written words (before: 416) | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |
| AC09 | `test_documents_name_the_same_parts_kinds_limits_and_rules`: the guide's rule table equals the helper's rule set; the contract names every rule ID with its limit, every kind and field; SKILL.md points at the guide; the example README covers the kinds example; no document claims a consumer migration | pass | `670238c425c0e2fcaa4475df9a1368c0eaac0f14` |

## Notes and limitations

- AC08's source question was read read-only from BetterPullReview's stored session
  under the user's attended-review state directory. Absolute paths were replaced with
  representative `/Users/reviewer/...` paths, and the example's images are placeholders;
  the real approved mockup and a capture of that frozen build were not embedded. Its
  build cannot yet open on a named surface, so one step still navigates (the RFC lists
  that consumer change as out of scope).
- A way to open an openable design artifact, and a Now image captured
  from the candidate, are authoring and self-check obligations; the helper cannot
  detect them. They are in the guide's kinds table and driver self-check.
- Native Windows and other browsers were not exercised; the runtime remains
  standard-library Python and the same page.
- Closeout review runtime: local implementer self-review; no independent review was
  required or run.
