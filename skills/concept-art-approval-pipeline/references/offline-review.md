# Offline Art Review Package

Resolve `concept_art_skill_root` to the absolute directory containing the loaded `SKILL.md`; run its bundled scripts by that path from the consumer working directory.

Use this package when an art review wave has multiple candidates or when the user needs durable, exact per-candidate decisions. It mirrors the useful interaction model of EWF-0116 without making art part of the ExampleWorkflow audio pipeline.

The page is deterministic and file-local. It copies review media into a portable directory, stores in-progress decisions in browser local storage, and exports a machine-readable verdict only when every candidate is resolved. The page cannot write repository evidence and its export cannot approve a later pipeline gate.

## Input Manifest

Create a JSON input manifest beside, or with paths to, the review media:

```json
{
  "schema_name": "sample_studio.art_review_batch_input",
  "schema_version": 1,
  "project_id": "example-project",
  "title": "Environment kit concept-source review",
  "review_gate": "concept_source",
  "candidates": [
    {
      "candidate_id": "art-candidate:/example-project/environment/sample-door/v003",
      "asset_key": "sample-door",
      "display_name": "Sample door v003",
      "description": "Example object with a clear silhouette.",
      "scene_role": "Contextual asset for a sample environment.",
      "acceptance_criteria": [
        "Matches the approved visual style",
        "Reads in isolation and at gameplay distance"
      ],
      "known_concerns": ["Check proportions against nearby assets"],
      "isolation_media": [
        {"label": "Front alpha", "path": "refs/sample-door/front.png"}
      ],
      "context_media": [
        {"label": "Environment mockup", "path": "refs/sample-door/context.png"}
      ],
      "identity_files": []
    }
  ]
}
```

Allowed `review_gate` values are:

- `concept_source`: approve an exact concept direction for art-bible integration and later source preparation.
- `generated_model`: review an exact generated model candidate. Put its GLB in `identity_files` and its preview in `isolation_media`.
- `texture_repair`: review an exact repaired GLB/texture pair. Put both files in `identity_files` and show de-lit comparisons in the media groups.
- `runtime_visual`: review an exact runtime visual candidate in isolation and project context. This remains separate from gameplay acceptance.

Every candidate requires at least one `isolation_media` item and one `context_media` item. Preview media may be PNG, JPEG, WebP, GIF, MP4, or WebM. `identity_files` may contain any exact artifact whose bytes must be bound to the decision, such as a GLB, texture atlas, or sidecar record.

`candidate_id` is stable semantic identity chosen by the project. The builder derives `candidate_digest` from the candidate metadata and SHA-256 digest of every isolation, context, and identity file. The resulting decision therefore names both the semantic candidate and its exact reviewed bytes.

## Build and Review

From the repository root:

```sh
python3 "$concept_art_skill_root/scripts/build_art_review.py" \
  build \
  --input /path/to/art-review-input.json \
  --out /path/to/art-review-package
```

Open `index.html` in a browser. The pinned review bar stays visible at every viewport width and reports reviewed, accepted, rejected, and pending counts. It also keeps the pending-only filter, final-copy action, and live copy result in reach while the user reviews long pages. The user can Accept or Reject each exact candidate, add notes, filter to pending items, and resume the same batch in the same browser. Storage keys include the batch ID, candidate ID, and candidate digest, so a revised file cannot inherit an earlier decision.

The export button remains disabled until every candidate is resolved. Do not treat browser-local state, screenshots, partial selections, or conversational phrases such as “approve the rest” as a verdict. Ask the user to copy the complete JSON export back to Codex.

## Validate the Export

Save the copied JSON to a temporary file, then validate it against the generated manifest:

```sh
python3 "$concept_art_skill_root/scripts/build_art_review.py" \
  validate-verdict \
  --manifest /path/to/art-review-package/art-review-manifest.json \
  --verdict /path/to/exported-verdict.json
```

Validation requires the exact batch and gate, an exact partition of all candidate ID/digest pairs, candidate-bound notes, and a complete false-only downstream claim set. After validation, apply only the accepted identities to the current gate’s normal integration procedure. Rejected identities remain evidence only.

The verdict schema is `sample_studio.art_isolation_review_verdict` version 1 and its scope is `human_visual_isolation_only`. It always leaves these claims false:

- art-bible integration
- source-generation readiness
- generated-asset approval
- texture-repair approval
- runtime promotion
- rights clearance
- in-game approval

The current gate’s normal integration and validation work may establish the next eligible state. The review page itself never does.
