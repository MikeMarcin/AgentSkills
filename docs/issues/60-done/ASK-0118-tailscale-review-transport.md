---
schema: implement-rfc.card.v1
id: ASK-0118
title: Prototype optional Tailscale Serve review transport
status: "Done"
rfcs: []
depends_on: []
priority: P1
metadata: {"milestone_plan":{"id":"attended-review-tailscale","path":"docs/rfcs/plans/attended-review-tailscale/milestone-plan.json"}}
acceptance: [{"criterion":"ASK-0118-TS01","outcome":"pass","revision":"b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131","evidence":{"kind":"artifact","path":"docs/rfcs/plans/attended-review-tailscale/verification.md","detail":"Foreground route lifecycle, occupied/concurrent-port refusal, two linked consumers, attach/mismatch, stop, handled termination and startup/runtime failures pass public CLI tests; first-use live consent and forced-kill limits remain explicit."}},{"criterion":"ASK-0118-TS02","outcome":"pass","revision":"b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131","evidence":{"kind":"artifact","path":"docs/rfcs/plans/attended-review-tailscale/verification.md","detail":"Exact Host/Origin/token rejection, missing POST Origin, forged localhost/forwarded Host rejection, separate review listener control denial, durable partial note/reconnect/handback, and HTTPS page behavior pass focused tests."}},{"criterion":"ASK-0118-TS03","outcome":"pass","revision":"b42654b4c8f8a1dd42ec20ebb5aa0bbb0f825131","evidence":{"kind":"artifact","path":"docs/rfcs/plans/attended-review-tailscale/verification.md","detail":"39 Python tests plus real-page JavaScript, docs and portable-source checks pass at the exact source candidate. Real disposable attempt reached human consent, status remained empty, fixture stopped/removed. Native HTTPS/mobile/Windows remain unobserved; no permissions or deployment performed."}}]
---

# Prototype optional Tailscale Serve review transport

Owner mandate, 2026-10-21: “Yes, my phone and remote machines are already on the
same tailnet. Let's prototype Tailscale Serve support for attended-review.”
Mandate revision `tailscale-prototype-v1`; assignment `/root/tailscale_prototype`;
run `tailscale-prototype-2026-10-21`, segment `implementation-1`. Baseline
`3ef1d0f0f44192d13311c1bac0d904cb19741a7a` (before product edits).

Own `skills/attended-review/**` and this compact independent follow-up's plan,
card and reservation. Preserve unrelated `.mask.lock.json`. Disposable scoped
Serve exposure is authorized. Keep loopback binding, durable intake and qualified
waiter/manual-resume behavior. No push/publication, credentials, permissions,
Funnel, daemon, consumer deployment, MASK internals or unrelated Serve changes.

Acceptance:

- **TS01:** Explicit optional foreground Serve exposes a private HTTPS root URL.
  Independent sessions select independent ports; existing mappings are inspected
  and collisions refuse. Same-checkout attach and local stop remain usable.
  Normal stop, interruption and startup failures reap owned processes without
  reset, broad teardown or persistent Serve settings. First-use enabling stays
  with the user; preserve its exact consent URL when supplied by Tailscale.
- **TS02:** HTTPS page uses the existing durable partial feedback/verdict/handback
  intake. Exact configured Host/Origin and session token remain required; forwarded
  headers grant no trust. Remote requests cannot stop the host or read its ping
  token. Existing limits, CSP, candidate fingerprints and CLI-only preparation hold.
- **TS03:** Meaningful fake-Tailscale lifecycle/failure tests, real HTTP/page checks,
  two symlinked disposable consumer contexts, focused regression and documentation
  checks pass. Record a real disposable Serve attempt and its actual limitation;
  phone/native tailnet acceptance remains explicit when not supplied. Document the
  experimental transport and exact launch/stop commands; commit explicit local
  paths and hand off quiescent command/writer state.

## Post-attended-review correction

Assignment `/root/tailscale_phone_closeout`, segment `phone-closeout-1`, same
`tailscale-prototype-v1` mandate. Original acceptance above is historical. The
coordinator reconciled phone feedback, explicit ACCEPT and handback cursor 12 at
`b42654b`; one item remained pending. The verdict concerns disposable transport
intake only; phone reload, automatic wake and native Windows remain unverified.

Native stop exposed shell-launcher process ownership: single-PID signaling left the
real Serve child outside graceful shutdown. Final source `f52a273e4058ae58f420c19bc2d2370fe857610d`
starts a separate POSIX process group, signals it with SIGINT and confirms eventual
removal of the exact foreground session. Seven focused public transport checks and
a fresh native macOS stop pass; helper exit 0, Serve {}, launcher/native child absent
and fixture removed. See this plan's verification.md and appended acceptance.json
records for exact candidates and the retained failed attempts.

The board helper refuses reopening terminal Done cards; this correction preserves
historical status/acceptance and appends the existing milestone's evidence without
bypassing that guard. No server/waiter or protected disposable candidate remains.
