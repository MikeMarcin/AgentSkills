# Hosted art decisions

Resolve the installed `attended-review` skill by name. Follow its question-authoring, serving and driver-wait instructions. The art package supplies the candidate identities and exact media. The companion supplies the human interface and saved decisions.

## Prepare and host

1. Build the canonical art package from the consumer’s input manifest. Keep the package directory, its manifest and the exact identity files available through handback.
2. Write one version-3 design question per independent candidate. Ask what the reviewer can judge in the images. Put original isolation stills in `now` and original context stills in `reference` as base64 data URLs. Put original videos in `media` with their role in the label. A video-only candidate also needs a representative still. Preserve the submitted bytes and protect the candidate paths.
3. In each question’s `metadata`, set `batch_id`, `candidate_id`, `candidate_digest` and `gate` from the canonical manifest. Set its `revision` to the literal batch ID, an `@`, and the candidate digest. An updated submission gets a new review binding.
4. Run the companion’s `check`, `init` and `prepare` against the consumer. Save its compact `status` as the prepared snapshot before sharing. Keep its session ID, sequence and question fingerprints in the driver’s private state.
5. Start `serve --tailscale` with the configured hub. Verify the live session is listed and the candidate pages load their source and context media. Give the reviewer the private URL and keep the host running. When the hub is unavailable, report the observed failure and the available review route.

## Take the handback

Read the same session’s `status --full --after SEQUENCE` at handback. Store the snapshot privately because it can include host capabilities. Keep feedback and skipped or withdrawn decisions in the session. The driver can act on explicit partial feedback while a full-batch verdict awaits the remaining decisions.

When each candidate has a saved accept or reject, run the art helper against the prepared and handed-back snapshots. Use the installed art skill location for the script.

```sh
python3 "$concept_art_skill_root/scripts/attended_verdict.py" \
  --manifest "$art_package/art-review-manifest.json" \
  --prepared "$private_state/prepared.json" \
  --handback "$private_state/handback.json" \
  --out "$evidence/art-verdict.json"
```

The helper checks the session, handback event, prepared question fingerprint, visible file bytes, exact art batch and gate. It preserves the saved notes and validates the usual gate-scoped verdict. Record the consumed event cursor after reconciliation. Export only the validated art verdict into project records. Keep session capabilities private.

If a hosted card displays a current in-scene render beside the isolation view in **Now**, keep the original snapshots and run the same command with `--context-in-now CANDIDATE_SHA256 IMAGE_SHA256`. Copy both digests from the canonical manifest, including their `sha256:` prefixes. Repeat the flag for each such still. The card must also show a distinct isolation still in **Now** and a separate submitted reference still in **Reference**. The helper verifies the render in its actual column and compares the outcome and latest feedback with the saved attendance events. Record the displayed placement and digests with the handoff so the verdict can be reproduced.
