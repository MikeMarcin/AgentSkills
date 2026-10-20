# Answer-adjacent review navigation verification

Assignment `/root/review_navigation`; mandate revision `review-navigation-source-v1`;
ASK-0116 NAV01–NAV03, one source-only milestone on AgentSkills main. Baseline:
`d19d11a84d841ec1aecf8c44d52cd27bc740e777`. Final source candidate:
`a7518cca7e2526dec8bf5eef5d87291232081af3`.

The answer area now has Next question and Finish and hand back. Next visits another
ready unanswered question in stable candidate-ID order, the same ordering used
inside the public queue's status groups. Answering or preparing a question therefore
does not change its place for navigation; reload and offline snapshots use the same
ordering. Navigation scrolls and focuses the heading at wide and narrow widths.
When no other ready question exists, Next is disabled and adjacent text explains
whether the current question can stay pending, preparation remains, or all questions
are answered. It never assigns a verdict.

Both handback buttons invoke one handler. It stops playback and flushes feedback
from every current candidate, including drafts retained on prior questions. A failed
save or a stale dirty draft prevents online handback and exposes recovery/export.
The adjacent message repeats the outcome where the reviewer pressed the button;
the existing masthead alert remains the single live error announcement. Offline
handback exports all partial answers and feedback. No browser or server protocol,
media transformation, candidate identity or feedback storage format changed.

## Direct evidence

- [Final real-page behavior checks](final-page-tests.json) pass at the exact source
  candidate: answered and pending navigation, server regrouping and reload,
  wide/narrow heading focus and scroll, disabled/end state, both handback
  entrypoints, failed prior-question draft/retry, playback stop, unanswered
  feedback retention, offline partial export and existing audio/feedback behavior.
- [Exact final-candidate Python/public-path run](public-tests.json): all 34 tests
  passed in 26.338 seconds, including real loopback HTTP, offline-page packet
  import, unanswered feedback, playback and handback regressions.
- `python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only`
  passed; relevant role source is unchanged by the navigation correction.
- Documentation validation after follow-up linkage correction: 16 RFCs, 116 cards,
  zero structural violations. The [terminal gate](terminal-documentation.json)
  passes after ASK-0116 is Done at `17a4406`. Scoped board validation and target-only
  plan discovery pass. `git diff --check` passed.
- Coordinator's native browser recheck at the exact final candidate: select answered
  Launcher A, use the lower Next question, arrive at Launcher B with `#title`
  focused and its top at viewport coordinate 0. Enter "Keep Launcher B pending;
  retain this feedback while moving on.", use lower Next, arrive at Launcher C with
  title focus/top 0. Lower Finish and hand back displays 1 answered, 7 unanswered,
  including 1 with feedback, beside the controls and at the masthead. Both Next and
  the lower Finish button are disabled. The enabled nearby controls are shown in
  [the browser screenshot](browser-navigation.png). This is an automated native
  browser observation, not a supplied human review decision. Narrow viewport focus
  and scroll are covered by the deterministic real-page model, not a separately
  resized native browser.
- [Public status corroboration](browser-observation.json): disposable session
  `3a06993c82fd45c40fdc4ad8f8d6cfc2`, sequence 28, one accepted Launcher A, seven
  pending, exact unanswered Launcher B note retained, all eight protected, durable
  handback set. Synthetic tones and tall text came through the canonical package's
  symlink in a disposable consumer and fixture-only registry.
- [Cleanup](cleanup.json): public stop succeeded; managed serve command exited 0;
  PID 52633 is absent, loopback port 54356 is closed, and the task-owned temporary
  consumer/registry/manifest were removed. No waiter, server or background command
  remains. Coordinator's screenshot writer completed before integration.

## Diagnoses and corrections

The initial real-page model passed at `be9072d`, but the coordinator's live browser
observed that answering Launcher A then pressing Next reached the brief instead of
Launcher B. Public `/api/status` groups answered questions at the end; the original
model did not reproduce this reorder. Candidate `a7518cc` removes that mutable
grouping from traversal, and the focused model now applies the public server's sort
and checks a reload. The initial [receipt](page-tests.json) is retained as partial,
insufficient evidence, not final acceptance.

The initial documentation gate correctly refused linking an unfinished follow-up to
terminal RFC-ASK-0016. ASK-0116 is now independent with related-RFC metadata and a
reference to the completed design. Original audio RFC/card/plan acceptance remains
unchanged. The binding was renewed after this scoped linkage correction, with no
other repository writers or uncertain command effects. An initial disposable
fixture-construction command failed on a missing optional `content` field before
initialization; using its empty-string default corrected the fixture only.

## Limits

This is source acceptance of the requested navigation UX. Automated synthetic
verdicts supply no human creative approval, asset rights clearance, or in-game
acceptance. Native Windows and native offline `file://` playback remain unperformed;
the prior RFC's limits remain unchanged. No deployment, consumer migration,
Faraday live-state change, publication, push or permission change occurred.
