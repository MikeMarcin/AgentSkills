---
name: sprite-sheet-animation-updater
description: Generate, update, integrate, and validate fixed-cell sprite-sheet animations for app or game mascots while preserving character identity, frame layout, transparent gutters, body scale, baseline, and horizontal registration.
---

# Sprite Sheet Animation Updater

Preserve the approved character model before adding effects or props. Resolve
bundled scripts against the absolute directory containing this `SKILL.md`,
including when it is installed through a personal or project MASK link.

## Establish the consumer contract

Read `<consumer>/.mask/skill-config/sprite-sheet-animation-updater/project.md`
when present, then follow its project-owned asset metadata and validation
commands. Keep character colors, cell dimensions, strip names, frame counts,
resource paths, generators, accessibility behavior, and build commands in the
consumer. Resolve those paths against the consumer, not the resolved skill link.

For a new consumer, inspect its runtime animation metadata and approved assets
to establish the same facts before generating or replacing a strip. Do not use
another project's mascot dimensions or color thresholds as generic defaults.

## Workflow

1. Select the cleanest approved frame or row as the character reference. Do not
   average across generated rows that have drifted from that model.
2. Record cell dimensions, row order, frame counts, padded columns, sheet size,
   resource names, and which clips loop versus play once.
3. Generate or revise one row at a time. Specify exact frame count, a single
   horizontal row, consistent scale and baseline, and a transparent background.
   Use the available image-generation skill for bitmap generation or editing.
4. Assemble fixed cells with transparent gutters. Measure the character body
   independently of props and effects; they must not determine body scale.
5. Composite transparent frames over the actual light and dark UI backgrounds.
   Check pale props, outlines, low-alpha shadows, glows, and theme contrast.
6. Validate nonempty active frames, dimensions, gutters, body width/height,
   horizontal registration, baseline, and loop seams. Allow body travel only
   where the clip intentionally calls for it; do not loop-seam test one-shots.
7. Update resource references, bundling, runtime animation metadata, and relevant
   regression tests together. Remove obsolete assets only after references end.
8. Run the consumer's existing image checks, focused tests, and resource build.
   Keep contact sheets and checkerboards as review output, outside runtime assets.

## Character consistency

- For body-locked fidgets, retain the approved neutral body and alter only the
  intended parts or overlays. Verify that blinks do not lift the feet and that
  moving props do not shift the body. Small accidental shifts read as hops.
- Keep intentional bounces inside their cells and return to the baseline where
  the clip calls for it. Review the last-to-first transition of looping clips.
- Keep first-run and transition clips separate from idle selection. Respect the
  consumer's Reduce Motion and mascot-placement rules.
- For an idle system with a base loop, fidgets, and flourishes, a weighted choice
  at the base-loop boundary avoids overlapping random timers. Follow existing
  product timing policy when it requires another approach.
- Avoid prop colors that contaminate the configured body-color detector.
  Review character expression and motion as well as static measurements.

## Generic validator

Use the bundled `scripts/validate_sprite_sheet.py` with explicit layout flags:
`--sheet`, `--cell-width`, `--cell-height`, `--columns`, `--rows`, and
`--animations name:frames,...`. `--json` returns machine-readable findings;
`--preview PATH` writes an optional inspection image.

The existing validator defaults are a **SampleCharacter-specific blue body detector** with
SampleCharacter-specific size and center ranges. For other characters use `--no-body-check`
and a consumer-owned body check, or explicitly supply suitable supported body
ranges. Disabling the body check does not verify character consistency.

Run the validator by its absolute installed script path from the consumer's
working directory. SampleAssets uses its self-contained
`tools/validate_sample_assets_character.sh` instead; its generator, runtime-strip list,
and full contributor contract remain in that repository.
