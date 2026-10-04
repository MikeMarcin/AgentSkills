---
schema: implement-rfc.card.v1
id: ASK-0105
title: Create frontend design for web, mobile and desktop
status: "Done"
rfcs: []
depends_on: []
metadata: {"milestone_plan":{"id":"frontend-design","path":"docs/rfcs/plans/frontend-design/milestone-plan.json"}}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"828e33b3b1cd1f39e7ae7ab4ea0aab9e34cba4a8","evidence":{"kind":"observation","detail":"Primary content review covers new interfaces, existing refinements and critique; scope and product conventions are explicit."}},{"criterion":"AC2","outcome":"pass","revision":"828e33b3b1cd1f39e7ae7ab4ea0aab9e34cba4a8","evidence":{"kind":"observation","detail":"Internal links reach web, mobile and desktop references with input, accessibility and runtime verification guidance."}},{"criterion":"AC3","outcome":"pass","revision":"828e33b3b1cd1f39e7ae7ab4ea0aab9e34cba4a8","evidence":{"kind":"observation","detail":"Skill metadata, repository structure, internal links and complete source catalog pass; final package has five original files and no upstream license or copied payload."}},{"criterion":"AC4","outcome":"pass","revision":"828e33b3b1cd1f39e7ae7ab4ea0aab9e34cba4a8","evidence":{"kind":"observation","detail":"MASK validated digest 3ed870536a0f6a064cce5dd6011fc3e85e11d2bb8fbde921f0d98fa86149b5ac; two isolated consumers passed status --check and both Claude/Codex links matched every package file."}}]
---

# Frontend design skill

Create an original `skills/frontend-design` inspired by the design ideas in the
user-supplied Anthropic frontend-design skill. Work directly in AgentSkills and
cover web, mobile and desktop UI with portable instructions.

User amendment on 2026-10-04: use the reference as inspiration, without copying
upstream text or including the Anthropic license. Replaced the initial adaptation
with original instructions and removed its copied license and adaptation notice.

## Outcome and acceptance

- AC1: A discoverable skill covers new interfaces, existing UI refinement and
  design critique without replacing the user's stack, brand or requested scope.
- AC2: Shared design guidance and reachable platform references cover web,
  mobile and desktop interactions, accessibility, content and visual verification.
- AC3: Package metadata, internal references, source catalog and documentation
  validate; the final package contains original instructions and no upstream
  license or copied payload files.
- AC4: MASK validates the actual package through a disposable local tap and
  resolves its content through links in two temporary consumer projects.

## Execution

Direct strategy; primary owns authoring, verification and bookkeeping. No model
delegation is used. Scoped host enforcement of delegation is not observed.
Initial plan discovery returned absent; the first binding attempt therefore
refused. A bounded one-milestone plan was then adopted for this card and bound
to the clarified user mandate.
No live installation, consumer migration or push is part of this request.

## Verification

- Skill Creator `quick_validate.py`: valid metadata and completed instructions.
- Repository `verify_documentation.py`: 15 RFCs, 105 cards, zero violations.
- Local inspection: all internal references resolve within the package; the
  source catalog covers every package; the final five files include no license,
  notice or copied upstream payload.
- MASK `skill validate` against a disposable local bare tap: valid payload,
  digest `sha256:3ed870536a0f6a064cce5dd6011fc3e85e11d2bb8fbde921f0d98fa86149b5ac`.
  Offline installation and `status --check` passed in two temporary projects;
  both Claude and Codex links resolved all five files byte-for-byte.
- Primary review covered new web UI, local component refinement, critique,
  native mobile and desktop-shell requests. Platform pointers select the relevant
  guidance; the entrypoint preserves requested scope and existing product choices.
  This was self-review, not an independent model trial or native application test.

The initial adaptation's fixture results were superseded by the original package's
checks after the user amendment. Its second fixture install had refused a stale
preview after the first install changed shared fixture state. Final verification
previewed and applied each consumer sequentially and passed.
