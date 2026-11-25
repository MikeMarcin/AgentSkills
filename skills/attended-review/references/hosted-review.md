# Hosted review

Use hosted review when an enrolled project chooses to store review material and
collect decisions on its hub. Hosted sessions use the hub collaboration page
for decisions and Hand Back. A hub can let designated reviewers hand back a shared review without waiting for the owner. The upgraded poller accepts both owner v1 and attributed reviewer v2 snapshots. The work machine can disconnect after publication.

## Configure a checkout

Resolve `REVIEW` to `python3 /path/to/attended_review.py --repo-root
/path/to/checkout`. Keep the same `--state` and `--registry` arguments for every
command if you use external runtime directories. The skill link and state
directory may live elsewhere. Routing comes from the selected checkout.

To opt new sessions into hosted review, place this JSON file at
`<checkout>/.mask/skill-config/attended-review/project.json`:

```json
{
  "schema": "attended-review.project.v1",
  "mode": "hosted",
  "hosted": {
    "origin": "https://producer.example.ts.net",
    "project": "design",
    "owner": "owner@example.invalid"
  }
}
```

Use the enrolled **producer** HTTPS origin, the project slug and the owner's
login on the collaboration origin. An installation slug is optional in the
file as `hosted.installation`. Omit it when operators use different installations
or keep it in a local profile for one enrolled checkout. For real internal
origins or account identities, keep the profile local and ignored, for example
using that checkout's Git exclude file. The config accepts no credential field.
MASK's selected skill and this separate checkout file serve different purposes.
A locked installation needs a source revision containing this feature before
it can read the file. Verify using the installed helper.

Run `REVIEW project-config` before first publication to inspect the selected
path, mode and normalized producer route. It reads the checkout without
creating a session or using credentials. Keep its output private when the route
contains internal information. Missing config defaults to legacy. A file can
also explicitly select legacy with
`{"schema":"attended-review.project.v1","mode":"legacy"}`.
A consulted file must be valid UTF-8 JSON with unique keys, at most 64 KiB,
and a regular file resolving within the checkout. Unknown fields, including
credential fields, fail the command without echoing their values.

## Prepare and publish

In a configured hosted checkout:

```text
REVIEW project-config
REVIEW init --manifest /path/to/manifest.json
REVIEW prepare --candidate caption --candidate layout
REVIEW hosted-publish --installation workbench --title "Release review" \
  --candidate caption --candidate layout
```

`init` reports `"mode": "hosted"` for a hosted session. On a new session,
`init --hosted` or `init --legacy` explicitly selects a mode without reading
the file. Existing sessions keep their mode even if the file changes or goes
away. Explicitly requesting a different mode requires a new state directory.
For a legacy session, follow the normal Serve, offline and optional
pass-through hub instructions.

For first publication, omit `--installation` if the profile supplies it.
Partial routing flags can restate matching profile values or supply an omitted
installation. To use a different route or publish without a profile, provide
`--origin`, `--project`, `--installation` and `--owner` together:

```text
REVIEW hosted-publish --origin https://producer.example.ts.net --project design \
  --installation workbench --owner owner@example.invalid --title "Release review" \
  --candidate caption --candidate layout
```

Check the intended route before passing the enrolled bearer credential through
`ATTENDED_REVIEW_HOSTED_TOKEN` to the publish and poll processes. The credential
needs `publish` and `handback` scope for the named installation and project.
The owner login needs owner access to that project on the collaboration origin.
The producer verifies the HTTPS certificate for the saved producer origin and
refuses redirects.

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
`REVIEW hosted-publish` again with no selection or enrollment flags. Retry and
poll use the saved route even if the project file changes or is removed. A
committed receipt contains the review ID and manifest revision. A different
package needs a new session directory. Open the enrollment's collaboration origin
and choose the published project and review ID.

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
manual reconciliation or start a new hosted review. If the old session holds
exclusive resources needed by the replacement, use its original checkout,
state directory and registry to run `REVIEW resume-development --candidate ID`
for each affected candidate. Then prepare the replacement. Owner export is also the
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
