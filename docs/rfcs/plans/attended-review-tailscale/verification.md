# Tailscale Serve prototype verification

Assignment `/root/tailscale_prototype`; mandate `tailscale-prototype-v1`; run
`tailscale-prototype-2026-10-21`, segment `implementation-1`; AgentSkills main.
ASK-0118 owns this independent ordinary-card prototype. Baseline before product
edits: `3ef1d0f0f44192d13311c1bac0d904cb19741a7a`.
Source candidate: `b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131`.

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
  interrupted by user changes and no bypass was attempted. The user's manual
  phone report remains pending. No native private HTTPS browser/phone acceptance
  or automatic waiter is claimed.
- The first added-test run exposed fixture assertions for omitted `host` when
  stopped, handback-only `feedback_pending`, and macOS `/private` path resolution.
  Assertions were corrected to the public contract; no runtime defect was inferred
  from those three fixture errors. The first live-recording wrapper similarly
  expected an absent host key; its rerun recorded cleanup successfully.
- Focused code-simplifier review simplified attach and child cleanup flow; no extra
  agent or independent review ran. Closeout review runtime: self-review only.

Verified real HTTPS HTTP-client requests now establish certificate-backed private
transport and durable partial intake after the user's manual setup. Native private
HTTPS browser/mobile reconnection and Windows process lifetime remain unobserved.
The coordinator owns the running demo and pending phone feedback; the original
`cleanup.json` records the initial implementation handoff, before that demo began.
No demo host, token or session identity is stored in Git. This evidence-only
follow-up changes no source and repeats no behavioral suite. The prototype does
not promise automatic model wake, friendly shared path mounts, access-rule changes
or survival after forced process death. A hard kill of the
Python parent can leave the Serve child alive; inspect its recorded PID and
foreground identity and stop only that verified process. See the skill's
[transport contract](../../../../skills/attended-review/references/tailscale-serve.md).

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
