---
schema: implement-rfc.card.v1
id: ASK-0105
title: Adapt frontend design for web, mobile and desktop
status: Ready
rfcs: []
depends_on: []
---

# Frontend design skill

Create `skills/frontend-design` from the user-supplied Anthropic frontend-design
skill. Work directly in AgentSkills. Preserve the source's deliberate visual
direction and extend it to web, mobile and desktop UI. Keep the package portable
and preserve source attribution and licensing.

## Outcome and acceptance

- AC1: A discoverable skill covers new interfaces, existing UI refinement and
  design critique without replacing the user's stack, brand or requested scope.
- AC2: Shared design guidance and reachable platform references cover web,
  mobile and desktop interactions, accessibility, content and visual verification.
- AC3: Package metadata, internal references, source catalog and documentation
  validate; the upstream license and source identity are retained.
- AC4: MASK validates the actual package through a disposable local tap and
  resolves its content through links in two temporary consumer projects.

## Execution

Direct strategy; primary owns authoring, verification and bookkeeping. No model
delegation is used. Scoped host enforcement of delegation is not observed.
There is no authored milestone plan; this card is the bounded outcome.
No live installation, consumer migration or push is part of this request.
