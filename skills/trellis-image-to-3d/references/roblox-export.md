# Roblox GLB export

The hosted providers produce a source mesh and preview. Keep both with the generation record. Export a lower-density copy with the intended grip or ground pivot, UVs, materials and any rig the target needs. A provider decimation setting describes the requested output. Measure the derivative that will actually enter Studio.

From the installed skill directory, run this command in Terminal or PowerShell with the project's Python interpreter. Substitute the real input and report paths.

```text
python scripts/trellis_client.py --audit-glb fighter-v002.glb --target roblox --audit-out fighter-v002.audit.json
```

The report binds the GLB SHA-256 and material-channel inventory to a list of mesh and primitive indices, names and triangle counts. Studio imports each glTF primitive as a MeshPart. The default limit is 20,000 triangles per part. Supply `--max-triangles-per-part N` for a smaller project budget, such as a creature that appears in a crowded lane. An oversized part, unreadable count or non-triangle primitive returns a failing exit code. Add `--pbr-required` only when the asset calls for those texture channels. [Roblox mesh limits](https://create.roblox.com/docs/art/modeling/specifications#geometry) · [Importer hierarchy](https://create.roblox.com/docs/studio/importer#gltf-import-hierarchy)

Counts come from the declared index accessor, or the POSITION accessor for unindexed geometry. The report measures each primitive definition once. Check actual instance counts, decoded textures, scale in studs, pivot, collision, animation and frame cost in the development place. Use **Concept Art Approval Pipeline** for the export decision and Studio binding when the project uses that workflow. [glTF mesh primitives](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#meshes-overview)
