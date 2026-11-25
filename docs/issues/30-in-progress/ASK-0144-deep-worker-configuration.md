---
schema: "implement-rfc.card.v1"
id: "ASK-0144"
title: "Update deep worker turn budget and Codex route"
status: "In Progress"
rfcs: []
depends_on: ["ASK-0046"]
---

# Update deep worker turn budget and Codex route

Increase the Claude deep worker cap from 56 to 200 turns to reduce forced
resumes. Request Astra 6.2 at xhigh for the Codex deep worker.

Verify the generated Claude and Codex adapters and the Codex companion
request using disposable fixtures.
