---
schema: "implement-rfc.card.v1"
id: "ASK-0011"
title: "Portable guided manual steps"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: []
acceptance: [{"criterion":"RFC-ASK-0003-AC04","outcome":"pass","revision":"wizard candidate from codex/portable-wizard based on 0cb7e6f","evidence":{"kind":"command","detail":"python -B -m unittest discover -s skills/wizard/tests: 8 passed on macOS and native Windows Python3.14.6; live browser save/agent advancement/pause persistence passed in disposable fixture."}}]
---

# Portable guided manual steps

Owned paths: skills/wizard/**.

Acceptance: RFC-ASK-0003-AC04; implement the approved design, preserve unrelated changes, verify focused public behavior and record actual results.

## Progress

Claimed for implementation.
