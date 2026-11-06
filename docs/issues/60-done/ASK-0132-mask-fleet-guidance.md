---
schema: "implement-rfc.card.v1"
id: "ASK-0132"
title: "Teach the canonical MASK skill to operate enrolled fleets"
status: "Done"
rfcs: []
depends_on: ["ASK-0005"]
acceptance: [{"criterion":"canonical-fleet-guidance","outcome":"pass","revision":"4a28361df3e56f08f2e1ed088aa3f9995e96dab9","evidence":{"kind":"observation","detail":"MASK capability inspection checked eleven public commands and flags. Public skill validation and approved install linked both adapters with exact committed skill and fleet reference bytes."}}]
---

# ASK-0132: Teach the canonical MASK skill to operate enrolled fleets

This follow-on to [RFC-ASK-0002](../../rfcs/RFC-ASK-0002-mask-management-skill.md)
covers canonical manage-agent-skills instructions. ManageAgentSkills MASK-0150
owns the runtime. Preserve the previous RFC's acceptance.

Add a fleet branch for enrollment, delegated taps, rollout and maintenance.
Use advertised commands, match preview hashes, preserve local grant boundaries
and inspect incomplete results. Validate the committed portable package and its
command options in disposable fixtures.

## Verification

Canonical package revision `4a28361df3e56f08f2e1ed088aa3f9995e96dab9` was read through the public
MASK CLI at `733df16981838e6b9b307cf6a0db80927b73d34c` from a disposable Git tap. The package validated,
and approved installation linked both adapters. Installed instructions and the
fleet reference matched the committed bytes. Advertised options matched all
eleven command shapes in the guidance. The fixture used local Git and temporary
consumer and machine directories.
