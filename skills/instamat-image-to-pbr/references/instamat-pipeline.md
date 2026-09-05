# InstaMAT Pipeline and Materialize Image

## Official surfaces

- Studio Materialize Image overview: https://docs.instamat.io/en/Products/InstaMAT_Studio/Materialize_Image
- Pipeline command-line reference: https://docs.instamat.io/en/Products/InstaMAT_Pipeline
- Materialize Image node reference: https://node.docs.instamat.io/latest/Library/Material/Scan%20Processing/Materialize%20Image.html

InstaMAT Studio provides the Materialize Image authoring UI. InstaMAT Pipeline is the documented console product for executing Atom and Element graphs without a GUI. Pipeline is a separate download exposed in the InstaMAT license portal when the license includes it.

## Discovery

The wrapper checks, in order:

1. `--pipeline`
2. `INSTAMAT_PIPELINE`
3. `InstaMATPipeline` on `PATH`
4. common macOS application locations

Use `doctor` to report Studio and Pipeline independently. The presence of `/Applications/InstaMAT Studio.app` does not prove that Pipeline is installed.

The official download guide states that Pipeline needs `-env` pointed at the Studio installation to access the InstaMAT Library. On macOS the wrapper automatically uses `/Applications/InstaMAT Studio.app/Contents/Resources/Environment` when present. Override it with `--environment` only for another valid package environment.

Use Pipeline's documented discovery modes directly when debugging:

```bash
InstaMATPipeline -mode Search -graphSearch "Materialize Image"
InstaMATPipeline -mode Info -graphInfo "Materialize Image"
```

For an external package:

```bash
InstaMATPipeline -mode Info /absolute/path/materialize.IMP -graphInfo "Materialize Image"
```

## Execution contract

Pipeline executes a graph with:

```text
InstaMATPipeline -mode Execute [Package.IMP] -graph Name Width Height
```

Graph parameter values are JSON. Filesystem resources use a `file://` URI encoded as a JSON string. Output filenames may contain InstaMAT variables such as `{OUTPUT.NAME}`.

The wrapper targets the official `Materialize Image` node and requests these material outputs:

- `BaseColor`
- `Normal`
- `Roughness`
- `Metalness`
- `AmbientOcclusion`
- `Height`

The documented input parameter is `Input`. Useful parameters include:

- `SharpenInput`
- `StrengthBaseColorShadowCancellation`
- `SharpnessBaseColorShadowCancellation`
- `Normal`
- `StrengthNormal`
- `Height`
- `AmbientOcclusion`
- `Metalness`
- `EnableNeuralSuperResolution`
- `ModeInputSeamless`
- `PreviewInputSeamless`

Inspect the installed graph with `info` before depending on optional parameters; node versions can change.

## Custom package fallback

If Pipeline's built-in library does not expose `Materialize Image` as an executable graph:

1. In Studio, create an Element Graph.
2. Add `Materialize Image` and expose its image input and required controls.
3. Connect and expose the six material outputs.
4. Save the graph in an `.IMP` package.
5. Pass that package to the wrapper with `--package` and the exposed graph name with `--graph`.

Keep the package beside project material tooling or in a dedicated pipeline package directory. Do not store it in the skill unless it is intentionally generic and redistributable.

## Output and engine integration

Generate 16-bit maps for review unless the target engine requires another format. Base color is color data; normal, roughness, metalness, AO, and height are non-color data.

For glTF ORM packing after approval:

- red: ambient occlusion
- green: roughness
- blue: metalness

Packing and GLB embedding are downstream integration steps. Preserve the unpacked source maps and the run record.
