---
schema: "implement-rfc.card.v1"
id: "ASK-0096"
title: "Update canonical RFC bundle install and uninstall handoff"
status: "In Progress"
rfcs: ["RFC-ASK-0015"]
depends_on: ["ASK-0095"]
acceptance: [{"criterion":"canonical-install-uninstall-reinstall","outcome":"pass","revision":"de0d3736f4767ac1af49f30f336f6a9c2bcd0314","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-install-uninstall-evidence.json","detail":"Exact source plus MASK d31bf5c installs four skills with reviewed setup and healthy status; 16 packages preserved; offline bundle uninstall retains manually selected grill-me; repeat no-op and healthy reinstall pass."}},{"criterion":"bundle-upgrade-policy-handoff","outcome":"pending","revision":"de0d3736f4767ac1af49f30f336f6a9c2bcd0314","evidence":{"kind":"observation","detail":"Owner version-policy choice pending through coordinator. Final upgrade guidance/verification and card completion remain open."}}]
---

# Update canonical RFC bundle install and uninstall handoff

Owner amendment, 2026-10-02, mandate `named-bundles-v2`: use MASK's public bundle
install/uninstall vocabulary. Own README, scripts/verify_rfc_bundle.py, bounded
canonical evidence and handoff records. Keep all 16 package discoveries and the
same four-skill bundle. Verify reviewed setup and healthy install, repeat no-op,
safe uninstall preserving a manually selected companion, and reinstall readiness
in a disposable consumer using an exact local source candidate and MASK runtime.
Individual skill install remains available. No publication, real deployment,
credential or permission changes. MASK-0128 owns runtime; do not duplicate its
mutable tracker. Historical ASK-0095 acceptance remains intact.

Owner follow-up "refresh seems like it should be upgade, no?": public vocabulary
install/uninstall/upgrade, mandate `named-bundles-v3`. Preserve historical evidence
and verify final exact command surface after the package-version policy is settled.

Quiescent partial handoff: canonical verifier completed successfully and its
TemporaryDirectory cleaned. No background commands, server, worktree or extra
writer remains. Required version policy choice is pending; resume on answer and
verify the changed upgrade scope before completing this card. Historical ASK-0095
evidence stays intact. No publication or actual running-host loading is claimed.
