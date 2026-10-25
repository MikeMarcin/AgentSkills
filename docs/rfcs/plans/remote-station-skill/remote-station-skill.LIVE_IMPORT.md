# Remote-station skill live import

Original immutable provenance: `docs/rfcs/drafts/RFC-DRAFT-0002-remote-station-skill.md`
(SHA-256 `20a902cc81188d7054d0784e5f478ba27a00def14237699f9375d9f4c4968d31`).
Mapping: RFC-DRAFT-0002 → RFC-ASK-0017. New cards from reservation
`ASK-0124--ASK-0127--8bd4f63309d8`: ASK-0124 (M1 AgentSkills skill), ASK-0125 (M2
AITO migration), ASK-0126 (M3 BetterPullReview migration), ASK-0127 (closeout). No
external handoffs: AITO and BetterPullReview work is done in their repositories
under their own trackers, and this board records only the RFC's acceptance.

RFC_BASE_SHA: `3ad85990719baec8f38544006a110c7a91bf6ab2` (before source edits). The
owner's 2026-10-24 directive to implement records acceptance (mandate revision
`remote-station-v1`). The draft's links were rebased from `drafts/` to the RFC root;
the text is otherwise unchanged.

Plan preparation was absent-plan preparation (`preparation-receipt.json`), adopted
from `proposal.json` into `milestone-plan.json`. Adoption first failed on Windows
because the provenance path used backslashes; commit `67c77e4` fixed that
implement-rfc defect before adoption succeeded.
