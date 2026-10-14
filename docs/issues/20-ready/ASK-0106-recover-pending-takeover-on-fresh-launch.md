---
schema: implement-rfc.card.v1
id: ASK-0106
title: Recover pending takeover before acquiring a fresh station lease
status: Ready
rfcs: []
depends_on: []
---

# Recover pending takeover before acquiring a fresh station lease

Owner mandate, 2026-10-13: fix BetterPullReview on JaegAW refusing
`python3 scripts/launch_remote_station.py --fresh` with
`finish pending local takeover before relaunch`. The previous ASK-0105/BPR-1401
hook removal explicitly retained that pending takeover.

Baseline: `4bdf12d49f0572e23d5d877b9655d977a4381ee0`.
Execution: direct primary, no delegated agents. Unrelated admission helper/schema
edits are outside this slice. Scope: shared launcher, takeover and supervisor
stop recovery, focused tests and directly relevant station instructions. Repair
the named WSL consumer through supported management; no publication or push.

- AC1: An explicit fresh launch retries a pending takeover before obtaining its
  new supervisor lease. Ordinary launches and unproven stops remain refused,
  with the public recovery command and original obligations preserved.
- AC2: A negative supervisor observation is retried; a matching completed
  controlled-stop receipt survives supervisor exit. A free lease, absent proxy
  or another holder's receipt never certifies a stopped runtime.
- AC3: Launcher/takeover/lease regression tests pass on Windows and WSL using
  disposable fixtures; the source manifest and documentation gate agree.
- AC4: The actual JaegAW pending takeover is completed after the owner's real
  stop confirmation, and the public fresh-launch path is exercised. Record
  the installed payload and any remaining runtime limitation explicitly.

Continuation: selected direct recipe; source ownership is limited to this card.
The owner confirmed the old station work is stopped in this chat. Supported
takeover returned local generation 3, pending null and a free lease. Native
fresh launch and focused regressions remain to be verified.
