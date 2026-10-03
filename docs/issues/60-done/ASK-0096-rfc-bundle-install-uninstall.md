---
schema: "implement-rfc.card.v1"
id: "ASK-0096"
title: "Update canonical RFC bundle install, uninstall and upgrade handoff"
status: "Done"
rfcs: ["RFC-ASK-0015"]
depends_on: ["ASK-0095"]
acceptance: [{"criterion":"canonical-install-uninstall-reinstall","outcome":"pass","revision":"39a6de558252eb0bf8c3cf9ae0d48f3fb10fa0ee","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-upgrade-evidence.json","detail":"All four RFC skills linked for both adapters, reviewed setup published and healthy; 16 packages discovered/validated; offline uninstall preserves manually selected grill-me, repeat no-op and healthy reinstall pass."}},{"criterion":"combined-upgrade-handoff","outcome":"pass","revision":"39a6de558252eb0bf8c3cf9ae0d48f3fb10fa0ee","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-upgrade-evidence.json","detail":"Named combined preview and guarded upgrade --all adopt a separately committed derived definition/package fixture revision; healthy status and repeat no-op pass. Exact MASK b879f8136489a98cfa26e0aae1da7e7e268c589b; 22 public commands overall."}},{"criterion":"companions-and-current-install-docs","outcome":"pass","revision":"39a6de558252eb0bf8c3cf9ae0d48f3fb10fa0ee","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-upgrade-evidence.json","detail":"README names grill-rfc companions, supported install/uninstall/combined upgrade/default and aggregate usage; individual installation remains. No obsolete apply/refresh command is advertised."}}]
---

# Update canonical RFC bundle install, uninstall and upgrade handoff

Owner amendments, 2026-10-02, mandate `named-bundles-v3`: public bundle
install/uninstall/upgrade; combined definition and newer unheld member versions;
include installed bundles in ordinary scoped upgrade and `mask upgrade --all`.
Owner explicitly answered "yes go with recommendation". Same authorized leaf and
preserved coordinator-implementer strategy; historical ASK-0095 acceptance stays
intact. MASK-0128 owns runtime; no duplicate mutable tracker.

Exact source candidate `39a6de558252eb0bf8c3cf9ae0d48f3fb10fa0ee` with MASK
`b879f8136489a98cfa26e0aae1da7e7e268c589b` passed the
[canonical public receipt](../../development/rfc-bundle-upgrade-evidence.json):
22 public commands, all 16 package discoveries/validation, all four RFC skills
linked for both adapters with reviewed implement-rfc setup and healthy status.
Offline bundle uninstall preserves manually selected grill-me; repeat no-op and
healthy reinstall pass. Named combined upgrade preview and guarded `upgrade --all`
application adopt a separately committed disposable definition/package update;
healthy status and repeat no-op pass. README retains individual install and names
grill-rfc companions.

The verifier completed and its TemporaryDirectory cleaned. No background command,
server, worktree or extra writer remains. No publication, real deployment,
credentials, permission changes or running-host loading is claimed. Native Windows
and actual host discovery remain outside this source-only handoff.
