# Session contract, versions 1 and 2

## External runtime state

For personal workflows, pass `--repo-root SOURCE --state RUNTIME/attended-review` on every command. The explicit state directory must be outside the source checkout; symlink resolution applies before this check. Session reuse refuses a different source checkout. Candidate path protection and preparation command working directories remain anchored to SOURCE. Use the same external `--registry` across cooperating drivers.


All commands print JSON. Errors print JSON to stderr and return 1. Supply `--repo-root ABSOLUTE_CHECKOUT` before the subcommand. The root is resolved, so both drivers pointing at the same checkout share its `.mask/attended-review/session.json`; separate Git worktrees resolve to distinct roots. The tool does not infer roots from installed skill links.

## Formats and compatible resume

Version-1 manifests and decision imports keep their established meaning, including
legacy `media` audio. Explicit audio questions require manifest version 2. The page
exports version-2 intake so older importers reject it instead of dropping feedback.
Reading a version-1 session does not change its bytes, fingerprints or verdicts.
An extension mutation upgrades state to `schema_version: 2`, identifies
`runtime_format: "attended-review.state.v2"` and `minimum_helper_version: 2`.
Resume that state with this version-2-compatible helper, using the same source,
state and registry paths; keep the upgrade with the session when transferring it.
An old helper is not a compatible downgrade. Future unsupported state versions refuse.

## Manifest

```json
{
  "schema_version": 1,
  "candidates": [
    {
      "id": "APP-0042-layout",
      "title": "Review the revised layout",
      "revision": "prepared-build-2026-09-05.2",
      "criteria": ["Labels are readable at the default window size"],
      "content": "Open the prepared build. Compare the default and narrow layouts.",
      "paths": ["app/ui/**", "fixtures/layout"],
      "resources": ["install:desktop-preview"],
      "prepare": {
        "speed": "quick",
        "argv": ["python", "scripts/prepare_preview.py"],
        "timeout_seconds": 300
      }
    }
  ]
}
```

Required: nonempty `id`, `title`, `revision`, and a nonempty string array `criteria`. Optional `content` is plain text, never evaluated Markdown or HTML. `paths` and `resources` default to empty arrays. `paths` are checkout-relative paths or glob patterns. Use forward slashes consistently in supplied paths. A directory path also protects its descendants. Glob matching uses Python `fnmatch` semantics: `*` can span separators, so choose narrow patterns. Protection is a coordination contract: agents query conflicts before mutations and judge which changes matter; it is not a filesystem watcher or mandatory rehash of the entire repository.

`resources` names shared devices, mutable installations, fixtures or other resources. Use stable canonical names (for example the resolved absolute installation path prefixed by `install:`), consistently across all drivers/checkouts on the machine. Different aliases for the same device cannot be detected automatically. Claims are exclusive by default, including different candidates within the same session. Preparing a command never shares another candidate's claim because it may mutate the resource.

An optional `resource_versions` map can share a **static** resource with the same explicit immutable version across candidates/checkouts:

```json
{"resources":["install:desktop-preview"],"resource_versions":{"install:desktop-preview":"build-abc123"}}
```

Both the existing and joining candidates must have no `prepare` command to share a claim. A preparation command owns an exclusive claim even if it declares the same resource version. The driver must truthfully identify the installed build and ensure it remains stable. Resources without matching versions conflict. Registrations are machine-local, at `~/.mask/attended-review-resources/`; all processes coordinating a resource must use that same directory. For fixtures or a configured shared location use `--registry PATH` or `ATTENDED_REVIEW_REGISTRY`. Remote device/farm ownership requires the repository's existing station adapter; this local registry does not coordinate disconnected machines.

`prepare` is optional. Without it, `prepare` makes already assembled static review material ready. With it, `argv` is a nonempty string array executed directly in the checkout without a shell; `speed` is `quick` (default) or `slow`; `timeout_seconds` defaults to 300, at most 86400. Only explicit CLI preparation executes commands; HTTP never does. Review these arguments as code and prefer existing repository tools. Logs remain in the session directory. Failed/conflicting preparations remain waiting with a concise reason while other candidates proceed. Preparation exit 0 records only that objective result. Use an adapter's readiness check or driver `ready --evidence` when a successful installer alone is insufficient.

Optional presentation:

- `options`: nonempty array of unique strings for a coupled selection group. The human selects one or more together; that group is one bounded decision. An independent acceptance should be a separate candidate.
- `launch`: `{label, command}`, and `copy`: labelled values the candidate asks to be pasted elsewhere. Both are shown for copying and never executed; both bind the candidate's fingerprint.
- `media`: array of `{kind: "image"|"audio"|"video", url: "data:image/png;base64,...", label: "..."}`. Inline data URLs make the offline file self-contained; keep evidence reasonably sized. For live applications the driver launches/captures directly instead of embedding a giant recording.
- `wizard`: textual `state`, `instructions` and optionally `url` for the standalone wizard companion. The driver prepares/opens its manual steps, observes its durable progress, then resumes review. This is a handoff, not a Python import dependency or automatic approval from wizard completion.
- `metadata`: descriptive information ignored for candidate identity and control flow.

`init --manifest FILE` adds/updates only listed candidates, preserving others and existing decisions. A SHA-256 fingerprint binds ID, revision, title, criteria, presentation and declared immutable resource versions; wizard host URLs, preparation metadata and unrelated repository HEAD do not invalidate it. Updating protected candidate material or protection definitions refuses until explicitly released. After release, changed material creates a new pending candidate and retains the old version/verdict in local history. Reusing unchanged material retains the decision; choose a new meaningful revision for an intentional new review. Unknown top-level candidate fields refuse rather than overwriting runtime state.

### Audio questions (manifest version 2)

Use the same candidate model and queue, with `question_type: "audio"` and an
`audio` object. Required text fields are `url` (inline `data:audio/...`), `purpose`
and `scope`; optional text fields are `variant`, `context`, `listen_for` and
`reject_if`. Existing `title`, `criteria` and `content` carry the question and
listening criteria.

Include a waveform preview for every audio clip by default; the user need not ask.
Reuse a trustworthy preview of the exact supplied clip, or prepare one with existing
available tools before `init`/`prepare`. Add a spectrogram when it helps judge
frequency content, noise, pitch or timbre. Choose readable time and
amplitude/frequency scales and label any excerpt so its relation to the clip is
clear. Preserve the reviewed audio bytes; preview preparation grants no authority
to normalize, trim or otherwise transform the clip, or to install dependencies.

Embed these producer-prepared images in `media` as self-contained inline data URLs.
They participate in candidate identity alongside the other judgment material;
descriptive provenance belongs in `metadata`. Check that each image represents its
exact clip and renders before publishing the candidate. If a trustworthy preview
or suitable tooling is unavailable, state the missing preview and reason concisely
in visible `content`, then continue with the playable review material. A missing
preview alone does not block review. Diagnostic images supplement listening and
establish no human verdict. The helper displays supplied images; its runtime
remains standard-library-only and generates no diagnostics.

Each audio question accepts or rejects one exact clip for that purpose. It cannot
have selection `options`. Optional `comparison_group` text links alternatives in
sequential navigation; it has no answer or protection semantics and does not bind
identity. Several clips may be accepted, or none; unanswered siblings stay pending.
The type, clip bytes and every supplied `audio` field bind the fingerprint, alongside
existing review material. Adding no new fields leaves legacy fingerprints unchanged.
Clip or purpose changes require explicit release, a meaningful new revision and
re-preparation. Previous feedback/verdicts remain in candidate history.

The player offers play/pause, native seek, replay from the beginning and an explicit
loop toggle. Playback requires reviewer action. Switching questions starts the next
clip at zero and pauses the previous one; pause and handback stop playback. Status
refresh and feedback saves preserve the active media element, position, playback,
text edits and focus. Playback/decode errors appear beside the player and as durable
`playback-error` events (offline diagnostics travel with the export). They establish
no answer or evidence that the reviewer listened. Timestamp insertion adds ordinary
text to feedback; it does not transform audio or create a second feedback system.

See [the portable example](../examples/README.md) for a mixed session.

## Commands and driver contract

| Command | Behavior |
|---|---|
| `init --manifest FILE` | Merge selected candidate definitions into the checkout's one session. |
| `prepare [--candidate ID] [--max-items N] [--include-slow]` | Publish static candidates first, then quick preparation, optionally slow. Each result is immediately durable. |
| `ready ID --evidence TEXT` | Driver records relevant preparation evidence and protects a candidate after its own adapter work. |
| `observe ID --evidence TEXT` | Append an objective observation; never a human decision. |
| `status [--after SEQUENCE] [--full]` | Compact candidate summaries include saved feedback, verdicts and playback errors; optional new events and full presentation/observations are available. Save the returned sequence as the driver cursor. |
| `start [--keep-preparing]` | Resume review and request cancellation of active prep by default. The current invocation stops, including its remaining queued preparation commands. Previously ready items remain available. |
| `pause` | Record a pause; preserve candidate protection and partial verdicts. |
| `hand-back` | The reviewer has finished. Records nothing; marks the session handed back and reports what was decided and what was left, including `feedback_pending` IDs for unanswered questions with saved feedback. `handed_back` clears again when a candidate is added or re-prepared, review starts, or resume-development releases candidates, so it describes only the current queue. |
| `wait [--after SEQUENCE] [--kind KIND ...] [--timeout SECONDS]` | Block until an event newer than the cursor of a requested kind exists (default `handed-back` and `decision`), print those events on one line and exit 0. A timeout exits 1 with the current sequence. Use `--kind handed-back` for the normal review boundary. Host orchestration follows [Driver waiting](driver-wait.md); process exit alone does not guarantee a model wake. It polls the file's modification time and reads under the ordinary lock only when that moves. |
| `conflicts --paths PATH ... --resources KEY ...` | Return overlapping local path/shared resource protections before modifying them. |
| `resume-development --paths PATH ... --resources KEY ... [--candidate ID]` | Release only selected affected candidates; unanswered ones become waiting. `--all` explicitly releases the whole checkout session. |
| `serve [--tailscale] [--tailscale-port PORT] [--tailscale-bin FILE]` | Start a foreground host or attach to this checkout's host. Agents choose `serve --tailscale` by default for every session under the [Tailscale contract](tailscale-serve.md); bare `serve` retains loopback for explicit local choice or deliberate fallback. |
| `stop` | Authenticate to and stop only the recorded host. Prepared candidates remain protected. |
| `html --output FILE` | Create standalone self-contained HTML after preparation. |
| `import --file FILE` | Validate and atomically intake partial answer/feedback JSON; `-` reads stdin. |

Prepare runs outside state locks, so other drivers and the UI can use already ready work immediately. Start/interruption cancels the current preparation invocation and its remaining queue, including interruption between commands. It cancels the current command tree (native Windows `taskkill`, POSIX process group). The cancelling item remains protected until the process exits and cleanup releases it. A command intentionally launching a detached/background installation must supply its own bounded adapter and cleanup; do not use such commands as generic prepare steps. Independent completed candidates remain ready. Ctrl-C retains prior progress.

`status` reports `waiting`, `preparing`, `cancelling` or `ready`, plus explicit decision/protection state. Preparation failures are waiting, not human rejection. New events are `candidate`, `preparing`, `ready`, `preparation-stopped`, `observation`, `decision`, `feedback`, `playback-error`, `handed-back`, `paused`, `review-start` and `resume-development`. Only `decision` is a user verdict; `handed-back` says the reviewer stopped, not that anything was approved. Complete acceptance in the authoritative board via the driver; never infer it from phase, pause or observation. If a host dies, decisions remain in the session file and `serve` replaces its stale host entry. Session hosts do not own protection lifetimes.

## Decision intake and offline fallback

Server UI POSTs each user decision immediately, even while no driver is running. Offline HTML retains local browser progress when storage is available and exports any partial set. Both feed this exact format:

```json
{
  "schema_version": 1,
  "session": "SESSION_ID_FROM_STATUS",
  "decisions": [
    {
      "candidate": "APP-0042-layout",
      "fingerprint": "FINGERPRINT_FROM_STATUS",
      "decision_id": "unique-id-for-this-verdict",
      "outcome": "accept",
      "note": "Optional human explanation"
    }
  ]
}
```

Outcome is `accept`, `reject` or `select`. `select` additionally requires a nonempty unique `selected` list from the candidate's options. Groups accept `select` or `reject`. Skip/pause produce no verdict. The user can review one candidate and leave all others pending. Repeating the same operation ID and content is idempotent, even after later edits. Reusing an ID with different content refuses. A new `decision_id` revises an answer and retains the previous submitted content in `superseded`/`decision_history`; `outcome: "withdrawn"` clears only the answer and retains feedback. A changed clip or judgment material uses a new candidate revision and preparation instead.

Intake validates session, candidate fingerprint and prepared/protected state, then atomically saves the supplied partial set. A malformed/stale set saves none of that set. It never requires all candidates to be decided. Offline exports include already completed decisions safely; a stopped or changed preparation may cause an old offline export to refuse, which requires checking what was actually reviewed rather than claiming new acceptance.

### Shared feedback and version-2 intake

All question types share feedback. Version 2 keeps the same `session` and
`decisions` array (which may be empty), plus optional `feedback` and `diagnostics`
arrays. An unanswered comment is a feedback entry, never a synthetic verdict:

```json
{
  "schema_version": 2,
  "session": "SESSION_ID_FROM_STATUS",
  "decisions": [],
  "feedback": [{
    "candidate": "death-C",
    "fingerprint": "FINGERPRINT_FROM_STATUS",
    "feedback_id": "unique-id-for-this-edit",
    "note": "Reject for death; consider for pain",
    "attachments": [],
    "expected_feedback_id": null
  }]
}
```

Feedback saves before an answer, across navigation, pause, page reload and host
restart. It does not increase the answered count. Submitting an answer includes the
current feedback, and the host files the answer's note as the current feedback
(`answer:` plus its `decision_id`). The page bases the next edit on that entry, so
a note typed after Accept or Reject, or before changing one to the other, is
saved with the answer rather than refused as a change made elsewhere. Editing
feedback on an answered question preserves its outcome, retaining prior feedback
and submitted answer content in history. Clearing feedback is an explicit empty
note/attachment save: the reviewer empties the note and removes each image, and
that edit saves like any other. Clearing an answer preserves feedback.
Reuse suggestions do not approve another use, create tasks or authorize integration.

Each feedback entry needs `feedback_id`, candidate and fingerprint; `note` defaults
to empty, `attachments` to empty. Answers/feedback accept at most four images, each
an object with nonempty `name` and inline `data:image/...` `data`. The per-image
bound is 4 MiB of data-URL text. The UI accepts source files up to 3 MiB so encoding
fits that bound. The whole CLI/HTTP intake is at most 20 MiB; use bounded partial
exports if needed. Limits are unchanged. Both arrays validate as one atomic set
against the session and prepared/protected fingerprint. A stale member saves none.
Optional `expected_feedback_id` on feedback or answers refuses an overwrite if the
current feedback ID differs (`null` means none); matching retries remain no-ops.
Exports omit this concurrency precondition so an offline set can be deliberately
reconciled by its driver after checking the candidate.

Live text edits debounce into session saves; navigation and handback flush edits.
The page has no separate save button: the note's status reads saving, saved or
not saved. A failed save retains the local draft, reports failure and offers
retry/export;
handback waits for a successful flush. A status refresh never replaces a dirty
editor. Browser storage failures warn that export is required. Offline storage is
only a convenience until the driver imports the partial version-2 export; offline
answer withdrawal is exported explicitly even for an answer embedded in the page.

The live page reads the whole session once. Inline images can make it megabytes
long, and re-reading all of it after every answer, over a slow tailnet link,
held Accept, Reject and Next disabled until it arrived. So every later read
(after an answer, a note save, pause, start or handback, and the 1.5-second poll)
asks `/api/status?material=omit`: each candidate's `media` and `audio`, which its
fingerprint binds, are left out and named in `material_omitted`, and the page
keeps the copy it holds for that fingerprint. Earlier answers and notes
(`decision_history`, `feedback_history`, `superseded`) are left out too. A
candidate whose fingerprint the page has not seen brings one full read. A poll
also names the sequence it holds (`after=SEQUENCE`) and is told only that
nothing changed; one poll runs at a time, and a reply older than the page's
state is ignored. A reply the page abandons by reloading or closing is dropped
quietly by the host.

Optional `diagnostics` entries hold candidate, fingerprint, `diagnostic_id` and a
nonempty `message` of at most 2000 characters. They record playback errors only,
with the same identity/prepared-state validation and idempotent operation rules.
They carry no verdict. Normal `wait --kind handed-back` ignores feedback and
playback activity; no driver/model loop is added.

The UI has direct Accept/Reject controls (Choose selected/Reject all for
options); the pressed control is the recorded answer, and pressing it again
records nothing new. A System/Light/Dark theme control is a browser preference
kept only in local storage; it is never session state, exported or logged. It has one-click partial export/copy/download and no large Markdown packet. Live API errors never display a false saved confirmation. Offline storage failures explicitly prompt export before closing. The session file is the durable record; browser localStorage is only a convenience cache until import.

## Local host and recovery boundaries

The printed URL carries a random token in its fragment. The page sends it as an Authorization header. The server binds `127.0.0.1` only, validates Host and browser Origin, limits intake to 20 MiB, denies arbitrary commands/files, disables remote content and framing with CSP, and never performs Git operations. Keep the URL private; do not publish host tokens. The default private HTTPS review follows the [Tailscale transport contract](tailscale-serve.md), including a separate loopback review listener and local-only controls. Separate worktrees/projects use separate session files and ephemeral ports. A second driver verifies the token before attaching to an existing host. Stopping one session cannot target another host.

Mutations use exclusive directory locks and atomic replace on both Windows and POSIX. Acquisitions are persisted before session readiness, and session invalidation is persisted before resource release. A conservative union of old and new claims bridges these writes, so an interruption leaves protection instead of admitting a conflicting preparation. Commands report a busy lock rather than guessing that a concurrent writer is dead. After an abrupt process kill, verify no controller/prepare command is using the affected lock before removing only its empty `.lock` directory. To clear a conservatively retained claim, use the owning checkout's explicit `resume-development --candidate ID` after restoring access; do not delete the entire registry or force another session through it. These are crash recovery steps, not routine approval checkpoints.

If a preparation controller is abruptly killed, its command tree may outlive it. Verify and stop that specific tree using the repository/native process adapter, then use `resume-development --candidate ID --preparation-stopped` to record that recovery attestation and release the stale preparation. This flag is not a normal cancellation shortcut; a live controller normally acknowledges `start`/`resume-development` itself. It does not kill an arbitrary stale PID.
