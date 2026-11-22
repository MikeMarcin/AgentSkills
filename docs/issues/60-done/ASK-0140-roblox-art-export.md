---
schema: "implement-rfc.card.v1"
id: "ASK-0140"
title: "Carry a TRELLIS export through Roblox Studio"
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"4dff85f4e71f163ef807cfff41dff632278391d8","evidence":{"kind":"observation","detail":"The public audit measured 12 triangles on Blender’s default cube and captured its exact digest. Fifteen TRELLIS tests passed, including independent primitives totaling above the cap, 20,000 and 20,001 triangle boundaries, non-indexed and indexed geometry, strips, fans, malformed counts, optional PBR, hosted provider compatibility and source-alpha preparation."}},{"criterion":"AC02","outcome":"pass","revision":"4dff85f4e71f163ef807cfff41dff632278391d8","evidence":{"kind":"observation","detail":"Six art review tests passed, including the hosted handback and the game_export identity changing with the derivative. Both skill entrypoints route to Roblox handling. The real Ribbonmarten plate (source SHA-256 4930c30728593e1f47ad9dbb61eff1058e687bff1d701ade772e07fc4ee5b60a) produced a source-alpha 768-pixel crop and a composited neutral RGB alternate. Studio acceptance remains attached to each consumer asset."}}]
---

# Carry a TRELLIS export through Roblox Studio

Add a Roblox path for projects using the concept approval and TRELLIS skills. Measure each candidate GLB against the importer’s per-mesh triangle limit and retain the distinction between local export evidence and an observed Studio binding. Existing provider and review workflows keep their current defaults.

## Acceptance

- **AC01** A local, opt-in audit reports the exact export digest and triangle count per glTF primitive. An over-budget or unmeasurable primitive fails. Existing PBR and provider modes still work.
- **AC02** Starting from either skill, an agent targeting Roblox can find the export check and trace the approved source to a Studio observation with the import hierarchy, scale in studs, pivot, collisions and material bindings.
