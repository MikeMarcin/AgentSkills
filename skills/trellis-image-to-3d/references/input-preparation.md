# TRELLIS Input Preparation

Use this reference when a concept-art source is a prop sheet, scene render, contact sheet, material board, or any image where the target object is not already a clean isolated object.

## Why Prepare

TRELLIS works best when the input is one object centered on a plain or transparent background. Art-bible sheets often contain several views, detail callouts, shadows, labels, and neutral presentation backgrounds. Send a single isolated view to TRELLIS instead of the full sheet.

## Preparation Command

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --prepare-image /absolute/path/source-sheet.png \
  --prepare-output-dir /absolute/path/trellis-input \
  --crop-box left,top,right,bottom \
  --output-stem target_name
```

The command writes:

- `target_name_crop.png`: the selected crop fitted onto a square neutral-gray canvas.
- `target_name_alpha.png`: the same image with connected neutral border background removed to transparency.
- `target_name_prepare-run.json`: the preparation manifest.

Use `target_name_alpha.png` for TRELLIS generation first.

## Crop Box Selection

Choose the largest useful object view and avoid material swatches, labels, inset details, and other views. For the ExampleScene sample object prop sheet, the proven crop was:

```bash
--crop-box 60,45,600,665 --output-stem sample_object_three_quarter
```

That selects the left three-quarter artifact view from `sample_object_sheet.png` and avoids the bottom material callouts.

## Alpha Cleanup

The preparation script removes background by flood-filling only neutral, border-connected pixels. It is intentionally conservative:

- Background eligibility uses HSV saturation/value thresholds.
- Pixels must connect to an image border to become transparent.
- Interior neutral object details are preserved unless they are border-connected.
- The alpha edge is lightly blurred to avoid harsh cutouts.

Default parameters match the ExampleScene sample object preparation:

- `--canvas-size 768`
- `--padding 64`
- `--background-rgb 128,128,128`
- `--alpha-sat-threshold 0.13`
- `--alpha-value-min 0.22`
- `--alpha-value-max 0.86`
- `--alpha-blur 1.1`

If the mask eats into the object, lower `--alpha-sat-threshold`, narrow the value range, or use the RGB `_crop.png` for generation. If background remains, use a tighter crop first; then consider raising `--alpha-sat-threshold` slightly.

## Generation Handoff

After preparation:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --image /absolute/path/trellis-input/target_name_alpha.png \
  --output-dir /absolute/path/trellis-output \
  --seed 0
```

Record both the preparation manifest and `trellis-run.json` with any generated model artifacts.
