# AgentSkills RFC tracker

Live RFCs are top-level `RFC-ASK-NNNN-*.md` files. Retained packets under `assets/` are immutable provenance, never a second live RFC/card index. Status vocabulary: Proposed, Accepted, Implementing, Implemented, Auto-Verified, Rejected, Superseded.

Only the main integrator imports, renumbers, edits tracker rules and confirms terminal status after integration. Each RFC has exactly one linked closeout card whose `closeout_for` includes the RFC. Store actual RFC_BASE_SHA before source implementation and record direct acceptance result/commit rows. Live board linkage selects work, not an arbitrary directory listing.

| RFC | Status | Title |
|---|---|---|
| RFC-ASK-0001 | Auto-Verified | Import and adapt the portable implement-rfc workflow |
| RFC-ASK-0002 | Auto-Verified | Agent-operated MASK management skill |
| RFC-ASK-0003 | Auto-Verified | Unified RFC implementation and attended workflow |

| RFC-ASK-0004 | Auto-Verified | Selected skill consolidation and consumer migration |

## Import and verification

Reconcile live IDs before adopting packet IDs. Keep original packet IDs in provenance and record a LIVE_IMPORT mapping including external handoffs. Never rewind counters or recycle reservations. Run `python scripts/verify_documentation.py --root .` after import/integration and before terminal status. When working a lane, status changes are proposals until the integrator revalidates them on main.

## Execution and usage pack

| ID | Status | Scope |
|---|---|---|
| RFC-ASK-0005 | Auto-Verified | Bounded deterministic execution and durable delegation |
| RFC-ASK-0006 | Auto-Verified | Project-aware turnkey usage capture and MASK selection |
| RFC-ASK-0007 | Auto-Verified | Reconciled usage accounting, account limits and task outcomes |
| RFC-ASK-0008 | Auto-Verified | Routing profiles, compact instructions and portable rollout |

| RFC-ASK-0009 | Auto-Verified | Standard implementation worker and independent review routing |

| RFC-ASK-0010 | Auto-Verified | Interactive coordinator and milestone integrators |

| RFC-ASK-0011 | Auto-Verified | Declared MASK workflow readiness for implement-rfc |

| RFC-ASK-0012 | Implementing | Authored milestone plans and outcome-bound continuation |
