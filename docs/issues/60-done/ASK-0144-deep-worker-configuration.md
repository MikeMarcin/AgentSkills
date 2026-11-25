---
schema: "implement-rfc.card.v1"
id: "ASK-0144"
title: "Update deep worker turn budget and Codex route"
status: "Done"
rfcs: []
depends_on: ["ASK-0046"]
acceptance: [{"criterion":"Generated Claude and Codex deep worker settings and Codex companion request","outcome":"pass","revision":"517bada5f1b18914ba3a56f475af07500a7b8a74","evidence":{"kind":"command","detail":"25 renderer tests and 12 Codex lane tests passed. Disposable Claude frontmatter contained maxTurns 200. Disposable Codex TOML and the fake companion request specified gpt-6.2-astra at xhigh. Portable source validation passed. Installed and running hosts were outside the verification scope."}}]
---

# Update deep worker turn budget and Codex route

Increase the Claude deep worker cap from 56 to 200 turns to reduce forced
resumes. Request Astra 6.2 at xhigh for the Codex deep worker.

Verify the generated Claude and Codex adapters and the Codex companion
request using disposable fixtures.
