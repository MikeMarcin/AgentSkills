---
schema: implement-rfc.card.v1
id: ASK-0118
title: Prototype optional Tailscale Serve review transport
status: "In Progress"
rfcs: []
depends_on: []
priority: P1
metadata: {"milestone_plan":{"id":"attended-review-tailscale","path":"docs/rfcs/plans/attended-review-tailscale/milestone-plan.json"}}
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
