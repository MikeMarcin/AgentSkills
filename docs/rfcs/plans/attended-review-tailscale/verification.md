# Tailscale Serve prototype verification

Assignment `/root/tailscale_prototype`; mandate `tailscale-prototype-v1`; run
`tailscale-prototype-2026-10-21`, segment `implementation-1`; AgentSkills main.
ASK-0118 owns this independent ordinary-card prototype. Baseline before product
edits: `3ef1d0f0f44192d13311c1bac0d904cb19741a7a`.
Original source candidate: `b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131`.
Post-review source candidate: `f52a273e4058ae58f420c19bc2d2370fe857610d`.

The optional `serve --tailscale` owns a foreground Tailscale CLI process on an
unused HTTPS port, mounted at `/`. The printed `url` is private HTTPS with the
existing fragment token; `local_url` remains available. Independent consumers
select independent ports, and existing persistent/foreground/Funnel/service uses
of a selected port refuse before mutation. A concurrent collision detected after
registration also refuses and stops only this process's foreground session.
No reset/off, Funnel, persistent background setting or access-rule change occurs.

A second loopback HTTP listener carries remote review. This is necessary because
Tailscale preserves the incoming Host header: allowing localhost Host on a shared
listener would let remote callers reach local control. The remote listener accepts
only the exact configured HTTPS authority/origin, requires Origin on POST, ignores
forwarded trust claims, retains bearer authentication on APIs, and denies ping/stop
regardless of forged Host. HTTP and HTTPS pages share the existing partial intake,
CSP, size bounds, fingerprints, preparation boundaries and qualified-wait contract.

## Evidence and limits

- `public-tests.json`: all 39 tests pass at the exact source candidate. New
  public fake-CLI/real-HTTP checks cover partial unanswered feedback and reconnect,
  handback, auth/Host/Origin rejection, missing POST Origin, forged forwarded Host,
  local-control denial, local attach/stop, mismatched transport refusal, occupied
  and concurrent ports, consent/startup failure, SIGTERM, runtime child exit and
  cleanup. Two disposable consumers invoke the canonical skill through separate
  `.agents/skills/attended-review` symlinks and retain independent host/session state.
- `page-tests.json`: the actual page script runs its established regression model,
  plus HTTPS online boot, partial note save and handback without a verdict. This
  is JavaScript behavior evidence, not a native browser/phone observation.
- `documentation.json` and `portable-source.json`: configured structure gate and
  portable source check. Scoped board validation, plan discovery and diff checks
  are included in closeout. No deployment/import or unrelated consumer migration.
- Real Tailscale 1.102.3 disposable attempt: the CLI reported that Serve is not
  enabled and returned its exact human consent URL. The helper exited 1, reaped
  the child, cleared its host and removed the disposable consumer. Serve status
  was `{}` before and after. Private raw receipt, including the exact consent URL:
  `/tmp/attended-review-tailscale-prototype/live-smoke.json`. The coordinator has
  the URL; no enabling, credentials or tailnet permission action was performed.
  This live attempt used the same transport implementation before final guard,
  metadata and malformed-status refinements; final exact-candidate regression is
  in the receipts above. It establishes the first-use gate, not HTTPS reachability.
- After the user explicitly authorized setup, they manually enabled HTTPS with
  Funnel unchecked. The coordinator observed certificate domains configured and
  Serve `{}` before starting a new disposable source-symlinked demo at the same
  source candidate. Real curl HTTPS root returned HTTP 200 with certificate
  verification result 0. Authenticated Python HTTPS `/api/status` returned 200
  with two candidates; HTTPS feedback POST followed by GET retained the exact
  submitted note on an unanswered candidate with no verdict. Sanitized results
  are in `live-attempt.json`; private raw receipts are
  `/tmp/attended-review-tailscale-prototype/live-https-status.json` and
  `/tmp/attended-review-tailscale-prototype/live-https-feedback.json`.
- The coordinator's real local IAB smoke saved an unanswered note, handed back,
  and reloaded with that feedback retained and zero verdicts. Private receipt:
  `/tmp/attended-review-tailscale-prototype/browser-smoke-status.json`. Private
  HTTPS IAB navigation timed out despite curl success; Chrome automation was
  interrupted by user changes and no bypass was attempted. At that evidence
  follow-up, the user's manual phone report remained pending. The later reconciled
  phone intake is recorded below; no automatic waiter is claimed.
- The first added-test run exposed fixture assertions for omitted `host` when
  stopped, handback-only `feedback_pending`, and macOS `/private` path resolution.
  Assertions were corrected to the public contract; no runtime defect was inferred
  from those three fixture errors. The first live-recording wrapper similarly
  expected an absent host key; its rerun recorded cleanup successfully.
- Focused code-simplifier review simplified attach and child cleanup flow; no extra
  agent or independent review ran. Closeout review runtime: self-review only.

## Post-attended-review correction and result

Assignment `/root/tailscale_phone_closeout`, segment `phone-closeout-1`, same
`tailscale-prototype-v1` mandate and private-transport milestone. Historical
acceptance remains bound to its original candidate; the appended acceptance
records bind this correction to `f52a273e4058ae58f420c19bc2d2370fe857610d`.

The coordinator reconciled the actual phone receipt through event cursor 12:
a note saved, `phone-note` received an explicit ACCEPT on fingerprint
`cb68c92e417699c41da95de530d927e82b5dbbcd9ebd1097003cf2a26f38f421`, and handback
left `remaining` pending. This is acceptance of the disposable transport intake,
not product approval. It does not independently establish a phone page reload.
The raw receipt stays private; Git contains no demo host, token, session identity
or user quote. The original demo is stopped and its fixture removed.

Real cleanup exposed an error after stop: the owned mapping still appeared after
the child PID exited, then a later status was empty. Extending the original roughly
two-second check to eight seconds alone failed a fresh native smoke at `7cfacd7`.
Single-PID SIGINT at `ba14c79` also failed after its three-second wait and kill.
The installed macOS CLI path is a shell launcher without `exec`; signaling its PID
did not reliably stop the actual foreground child. Tailscale 1.102.3's
[Serve source](https://github.com/tailscale/tailscale/blob/v1.102.3/cmd/tailscale/cli/serve_v2.go#L374)
handles `os.Interrupt` and defers foreground watcher closure. This supports using
Ctrl+C signaling; it does not establish an exact daemon expiry time.

The final correction starts an owned POSIX process group and sends it SIGINT,
retains the three-second kill fallback and an eight-second monotonic exact-session
removal check, and leaves unrelated mappings untouched. A shell-launcher fixture
requires SIGINT for cleanup; separate public CLI regressions cover delayed removal
after child exit and a genuinely lingering session that still fails.
`post-review-transport-tests.json` records all seven focused transport tests passing
at the final exact candidate, including two linked consumers and HTTP boundaries.
No client code changed; the earlier page regression and unchanged baseline checks
remain applicable. Closeout review runtime: self-review only.

`post-review-native-stop.json` records the final fresh native macOS pass: empty
Serve prestate, exact owned mapping registered, local stop acknowledged, foreground
helper exit 0 in 0.238 seconds, empty Serve status, both shell launcher and actual
native child absent, and disposable fixture removed. Earlier failed native attempts
remain sanitized in `live-attempt.json`. No reset/off, setup, credential, permission,
Funnel, publication, deployment or push action occurred in this round.

The board helper refuses reopening terminal Done ASK-0118. This original-milestone
correction therefore appends evidence to its existing card without bypassing that
guard or creating new scope. Documentation/scoped board checks accompany closeout.
Phone reload, automatic agent wake and native Windows lifetime remain unverified.
Forced parent death may still require verifying and stopping its owned CLI process
group; friendly shared path mounts remain outside the prototype. No live server,
waiter or protected disposable candidate is handed off.

## Disposable demo after user setup

The coordinator can run the following on the source host. It creates a new consumer
through a symlink, uses a private fixture registry, and prepares two static choices.
The source checkout stays unchanged. Keep the printed directory for stop/cleanup.

```sh
review_demo_root="$(mktemp -d /tmp/attended-review-tailscale-demo.XXXXXX)"
python3 - "$review_demo_root" <<'PY'
from pathlib import Path
import json, sys
base = Path(sys.argv[1])
consumer = base / 'consumer'
consumer.mkdir()
link = consumer / '.agents/skills/attended-review'
link.parent.mkdir(parents=True)
link.symlink_to('/Users/jaeger/Documents/GitHub/AgentSkills/skills/attended-review', target_is_directory=True)
manifest = {'schema_version': 2, 'candidates': [
    {'id': 'phone-note', 'title': 'Save a note from your phone',
     'revision': 'b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131',
     'criteria': ['A note saves and survives a page reload'],
     'content': 'Disposable transport demo. Type a note, leave this question unanswered, reload, then finish and hand back. This tests intake only.'},
    {'id': 'remaining', 'title': 'Leave this question pending',
     'revision': 'b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131',
     'criteria': ['Pending questions remain pending'],
     'content': 'No answer is required. Partial review is enough.'}
]}
(base / 'manifest.json').write_text(json.dumps(manifest))
print(base)
PY
python3 "$review_demo_root/consumer/.agents/skills/attended-review/scripts/attended_review.py" --repo-root "$review_demo_root/consumer" --registry "$review_demo_root/registry" init --manifest "$review_demo_root/manifest.json"
python3 "$review_demo_root/consumer/.agents/skills/attended-review/scripts/attended_review.py" --repo-root "$review_demo_root/consumer" --registry "$review_demo_root/registry" prepare
python3 "$review_demo_root/consumer/.agents/skills/attended-review/scripts/attended_review.py" --repo-root "$review_demo_root/consumer" --registry "$review_demo_root/registry" serve --tailscale --tailscale-bin /usr/local/bin/tailscale --tailscale-port 8443
```

Use the complete printed HTTPS URL on the tailnet device. Existing port 8443 use
refuses; select another already-permitted unused port explicitly if needed. For
local-only preview, run plain `serve` instead. From another command session with
`review_demo_root` set to the printed directory, inspect `status`, or invoke
`wait --after SEQUENCE --kind handed-back` only through the qualified host contract.
The coordinator owns any waiter; no waiter/server is handed off by this milestone.

Stop through the same linked helper:

```sh
python3 "$review_demo_root/consumer/.agents/skills/attended-review/scripts/attended_review.py" --repo-root "$review_demo_root/consumer" --registry "$review_demo_root/registry" stop
```

Wait for the foreground command to exit, inspect `tailscale serve status --json`,
then remove only that disposable directory through the normal fixture cleanup.
Saved decisions remain in its session until cleanup; import/copy any desired demo
evidence first. No live token, full private status or phone verdict belongs in Git.

## Subsequent awake Codex handback qualification

The `remote-review-standard-v1` instruction milestone incorporates a later real
phone handback at source `38d0715610fa9255fdf990067c43b669c7d54191`, whose helper
runtime last changed at `f52a273e4058ae58f420c19bc2d2370fe857610d`. The complete
sanitized runtime/measurement summary now lives with the portable
[Driver waiting qualification](../../../../skills/attended-review/references/driver-wait.md#recorded-awake-runtime-qualification)
so a matching driver can reuse the known-good recipe without a fresh probe.

The inner handback-only waiter ignored a saved intermediate decision. One outer
tool call stayed pending until the actual phone handback and returned once with
exit 0 and the expected session. Session identity, candidate fingerprints and the
new cursor were reconciled and consumed before dispatch. No assistant activity or
token-count usage events were recorded during the blocked outer call; handover/
arming activity occurred before that interval. The owned waiter/server/Serve
processes and fixture were cleaned up. No private IDs, host/token, raw quotes,
paths, timestamps or usage totals are copied into this receipt.

This supersedes the earlier automatic-wake gap for the recorded short awake
runtime only. Historical failed cleanup attempts and incomplete extended waiting
remain as recorded. Phone reload, overnight waiting, sleep/app restart and native
Windows are still unverified. This documentation-only milestone starts no server
and repeats no native acceptance test.
