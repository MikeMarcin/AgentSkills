# Private HTTPS for remote review

Use Tailscale Serve as the standard transport when the reviewer is on a phone or
another device, or the session runs through SSH, remote control or Dot. A remote
review request authorizes its temporary scoped private Serve session; use that
authority without repeatedly requesting separate transport approval. Review at the
source computer uses loopback. The CLI's bare `serve` default remains loopback;
select `--tailscale` for this remote branch.

Tailscale must already be installed, signed in and online, with HTTPS enabled and
the reviewer able to reach this device through existing access rules. If a
prerequisite is missing, surface the exact setup requirement or CLI error. Setup,
installation, access grants and HTTPS permission changes remain separate user
decisions; the review request does not authorize them. The helper changes none of
those settings and never enables Funnel.

From the selected consumer, initialize and prepare the usual manifest, then run:

```sh
python /path/to/attended-review/scripts/attended_review.py --repo-root /path/to/consumer serve --tailscale
```

Use a supported local Python executable. If Tailscale is outside PATH, add
`--tailscale-bin /absolute/path/to/tailscale`. Choose an unused HTTPS port already
permitted by the tailnet's access rules; pass `--tailscale-port PORT` when selecting
it explicitly. Omitting that flag uses this host's OS-assigned loopback port; it
must also be permitted, and may require a different link after restart.
The helper never opens firewall rules or changes tailnet access to make a port work.

Open the complete printed `url`, including `#token=...`, on the other device.
`local_url` continues to work on the source machine. Treat either URL as a private
session capability; keep tokens out of commits, public links and review content.
The printed `tailscale` record identifies the HTTPS origin, port, owned foreground
session and child PID. Route registration is checked before printing the URL;
that check alone does not establish certificate issuance or remote reachability.

If Tailscale prints a first-use consent URL, the helper returns it as an error and
stops its attempted host and child. Give the exact URL to the user and leave the
permission decision with them, then retry the same command after they complete
setup. Review any requested HTTPS or other permissions before enabling them.
A failed attempt leaves prepared candidates and durable feedback available; run
plain `serve` for local review while setup remains pending.

## Lifetime and isolation

The helper invokes `tailscale serve --bg=false --https=PORT http://127.0.0.1:BACKEND`.
It keeps both HTTP listeners bound to loopback. Serve proxies only the separate
review listener; local ping/stop controls are unavailable there even if a caller
forges localhost headers. The review listener permits only the configured exact
HTTPS Host and Origin, requires Origin on POST, and retains the session bearer
token on every API request. Forwarded and Tailscale identity headers grant no
additional authority. Existing CSP, intake bounds, fingerprints and CLI-only
preparation apply to both listeners.

Each host owns a whole HTTPS port mounted at `/`. Existing persistent, foreground,
Funnel and service mappings on that port cause refusal before mutation. Independent
checkouts use independent backend ports and must choose different HTTPS ports.
This intentionally keeps root-relative API URLs; friendly shared `/reviews/...`
mounts are unsupported. Another driver in the same checkout attaches to
the existing host without changing Serve. Changing its transport or explicit port
requires stopping that host locally and starting it again.

Keep the source machine online and the foreground helper running. Saved partial
feedback and answers live in the same durable session files; closing the browser,
reconnecting or leaving other questions unanswered does not lose saved intake.
Unsaved browser drafts still need retry or export, especially before changing a
URL's origin. Before presenting the full HTTPS capability link, arm automatic
continuation through [Driver waiting](driver-wait.md). The host must stay awake
with the foreground helper and tool connection live; use its explicit manual-resume
fallback when a qualified wait is unavailable.

Stop from the source machine with the same source/state/registry arguments:

```sh
python /path/to/attended-review/scripts/attended_review.py --repo-root /path/to/consumer stop
```

Local stop, Ctrl+C, handled termination and startup/runtime failures reap the owned
Serve child and close both listeners. Cleanup relies on Tailscale's foreground
session lifetime. On POSIX, the helper starts a dedicated process group and sends
it SIGINT so Serve can close its foreground watcher through its Ctrl+C handler,
including when the CLI path is a shell launcher. A group whose launcher does not
exit is killed after three seconds. Native Windows termination remains separately
unqualified.
Cleanup never runs `reset`, unscoped `off`, `--bg`, or Funnel. If cleanup
cannot confirm removal after polling the exact session for up to eight seconds,
inspect `tailscale serve status --json` before retrying. The local `stop` response
acknowledges shutdown; wait for the foreground helper to finish before checking
cleanup or starting another host.
A forced kill of the Python process, host crash or native Windows termination may
skip Python cleanup. Inspect the recorded child PID, foreground session and route;
stop only the verified owned CLI process through the native process tools. Never
reset another owner's Serve settings to recover. Tailscale itself removes the
foreground mapping when that CLI's session ends.

Focused fake-CLI, real loopback HTTP and HTTPS page regression coverage is
supplemented by observed private HTTPS certificate validation, phone save/accept/
handback, and native macOS scoped stop with Tailscale 1.102.3. The awake Codex
handback qualification is recorded in [Driver waiting](driver-wait.md). These
bounded observations do not establish phone reload, native Windows lifetime,
overnight waiting or recovery across sleep/app restart.

Protocol references: [Serve](https://tailscale.com/docs/features/tailscale-serve),
[CLI flags and lifetime](https://tailscale.com/docs/reference/tailscale-cli/serve),
[examples](https://tailscale.com/docs/reference/examples/serve). The implementation
was checked against Tailscale 1.102.3, including its foreground configuration and
preserved proxy Host behavior; it uses the CLI rather than an internal daemon API.
