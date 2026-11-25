# Hosted review

Use hosted review when an enrolled project chooses to store review material and
collect decisions on its hub. Create a new session with `init --hosted`.
The mode is fixed at initialization. Hosted sessions use the hub collaboration
page for decisions and Hand Back. The work machine can disconnect after publication.

## Prepare and publish

Use the usual manifest, preparation and resource protection commands. In these
examples, `REVIEW` stands for `python3 /path/to/attended_review.py --repo-root
/path/to/checkout`, with the same `--state` and `--registry` options every time
if you use external runtime directories.

```text
REVIEW init --hosted --manifest /path/to/manifest.json
REVIEW prepare --candidate caption --candidate layout
REVIEW hosted-publish --origin https://producer.example.ts.net --project design \
  --installation workbench --owner owner@example.invalid --title "Release review" \
  --candidate caption --candidate layout
```

Give the publish and poll processes the enrolled bearer credential through
`ATTENDED_REVIEW_HOSTED_TOKEN`. The credential needs `publish` and `handback`
scope for the named installation and project. The `--owner` login must have
owner access to the project on the collaboration origin. The producer uses
verified HTTPS to the saved Tailscale Serve origin.

Repeat `--candidate` in review order. Each selected candidate must be prepared,
protected and unanswered. Select candidates whose displayed titles, criteria,
options and text are suitable for sharing with the project. Text can include
legacy content, the question's Why, document and note, and audio instructions.
`--include-media` adds those candidates' inline PNGs and PCM WAVs that meet the
hub's size and format limits. `--include-links` adds their HTTPS links with
no credentials, queries or fragments. The package omits local paths,
launch and preparation commands, step values, feedback, existing decisions,
and installation credentials. Keep sensitive information out of all selected
display text and assets.

The command saves the exact manifest and selected media locally before its
first request. If staging, upload or commit is interrupted, run
`REVIEW hosted-publish` again with no selection or enrollment flags. A committed
receipt contains the review ID and manifest revision. A different package needs
a new session directory. Open the collaboration origin and choose the project
and review shown by the receipt.

## Receive Hand Back

After the owner selects **Freeze and hand back** on the collaboration page,
run `REVIEW hosted-poll` from the original checkout using its original session
directory. Restoring a database backup requires that same directory. A copy in
another directory cannot receive or acknowledge the review. A poll returns
`waiting` if the hub has no queued delivery and the origin has no receipt. A valid frozen
delivery adds the owner's current decisions and the Hand Back marker to
the native session. It writes searchable `session.json` through that marker
before acknowledging delivery and returning `delivered`. Existing JSON readers
can open a copy of this archive. Keep the active SQLite database and its
archive together for recovery.

Repeat `hosted-poll` after interruption. The saved delivery lets the command
recover archive creation or retry an ACK without adding duplicate decisions
or a second Hand Back marker. For a recorded delivery, every poll checks the
archive and confirms the matching ACK with the hub. This also restores delivery
status if the hub was restored to a backup taken before acknowledging it.
Use `status --after SEQUENCE` with the consumed
cursor to reconcile the decision events and marker. The hub retains attributed
collaboration feedback in the review and audit views.

If the hub reports **Needs attention**, inspect the original session. A
candidate that lost protection must be prepared again against the same
fingerprint. If a restored origin database lacks the local delivery receipt
and the hub still has the frozen delivery queued, the helper checks any existing
`session.json` against the exact archive it would write. It keeps a matching
file in place. Preserve a conflicting file elsewhere before retrying. For
material that has changed, use a new hosted session for a new review.

Earlier hosted databases without a directory binding cannot publish or receive
an ACK. Preserve the database and any archive. For an unpublished draft, use
its manifest to start a new hosted session in a separate state directory. For
a published review, ask the enrolled owner to export the frozen result for
manual reconciliation or start a new hosted review. Owner export is also the
recovery path when the hub has already acknowledged the delivery and the
restored origin lacks its receipt.

## Local integration verification

```sh
ATTENDED_REVIEW_HUB_ROOT=/path/to/AttendedReviewHub \
  python3 -B -m unittest discover -s skills/attended-review/tests -p test_hosted_review.py -v
```

The fixture uses real hub backends with temporary data and private sockets,
with loopback HTTPS as the front door. The fixture connector
`ATTENDED_REVIEW_HOSTED_FIXTURE_CONNECT=127.0.0.1:PORT` overrides the TCP
destination only. TLS still verifies the configured producer name against
the trusted certificate. Run this fixture with `openssl` and both local
source checkouts available.
