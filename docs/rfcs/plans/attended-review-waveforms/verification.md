# Default audio waveform preparation verification

Assignment `/root/waveform_guidance`; mandate `waveform-guidance-source-v1`;
ASK-0117 WAVE01–WAVE03; one source-only `default-previews` milestone on AgentSkills
main. Baseline `d72887ef3d79d71e4029d3146b85bdf55fbbf55d`; source candidate
`a1d3d6cf7af83e51a4111b144673940f01cb4cd2`.

## Guidance and pruning review

The main skill's audio branch reaches the contract before preparation. The contract
owns the default waveform rule, useful-spectrogram condition, exact-clip preparation
and explicit missing-preview fallback. The main skill retains only a branch pointer;
its former duplicate answer-unit/comparison explanation is already in the contract.
The example README describes its fixture and points back to the authoritative rule.
No renderer, helper runtime, dependency, audio payload or intake format changed.

Self-tabletop of the preparation path (not an independent agent trial):

- Ordinary review: steps 1–3 reach the existing manifest/preparation path; the audio
  branch adds no diagnostic work.
- Audio with an existing exact-clip waveform: step 2 reaches Audio questions, reuses
  the trustworthy inline image, checks rendering/clip correspondence and prepares.
- Audio without a preview: that same branch prepares a waveform with available tools
  without a separate user request. A frequency/noise/pitch/timbre question adds a
  spectrogram when it helps judgment.
- Unavailable trustworthy preview/tooling: visible content names the missing preview
  and reason, then proceeds with playable material. No dependency installation or
  audio transformation follows from this instruction. The intentionally broken
  example visibly explains why no waveform can be prepared.

The checks exercise the intended branch order and exceptions; they do not measure
future model compliance. Self-review found no duplicated authoritative rule or need
for a general media pipeline. The SVG helper is specific to its known 8-bit mono
synthetic fixture; it plots extrema across all samples, with full-scale amplitude,
a full-clip time axis and no resampling or audio changes.

## Direct example and source checks

[Example receipt](example-checks.json) binds the exact source candidate. A disposable
fixture linked the canonical package into two distinct consumer roots and used one
fixture-only resource registry. The public commands were:

`python3 -B .../examples/mixed_audio.py --output MANIFEST`, followed by the linked
`.../scripts/attended_review.py --repo-root CONSUMER --registry FIXTURE_REGISTRY`
with `init --manifest MANIFEST`, `prepare`, `html --output HTML`,
`resume-development --all`, and `status`.

Both isolated sessions prepared eight candidates with zero answers. The generated
HTML retained all six exact inline SVG URLs and the broken-clip limitation. All
fixture protections were released. No live host was started.

A focused stdlib check decoded each generated WAV: 8-bit mono, 8000 Hz, 96,000 samples.
Every one of the 600 SVG envelope columns was checked against the exact minimum and
maximum of its 160 samples. All six audio data URLs equal the baseline's, and removing
the media changes the existing canonical fingerprint. XML checks found self-contained
SVG without scripts or external references. Existing ImageMagick rendered all six
SVGs using the existing system Helvetica font; the [contact sheet](example-waveforms.png)
was inspected locally. The coordinator separately inspected Launcher A: title,
amplitude labels and 0–12 s axis are legible, with the expected steady tone envelope.
These are image observations, not human creative acceptance or browser qualification.

`python3 -B scripts/verify_documentation.py --root .` passed: 16 RFCs, 117 cards,
zero structural violations. `python3 -B skills/implement-rfc/scripts/validate_portable_agents.py
--source-only` reported portable source valid. Scoped board validation, target-only
plan discovery and `git diff --check` passed. No broad suite or wording assertions
were added for the prose change.

## Diagnoses, cleanup and limits

Before plan adoption, discovery/preparation refused the not-yet-created live-plan
pointer. The bounded proposal was adopted explicitly; discovery then succeeded.
The retained preparation receipt is a refusal, not a passing preparation claim.
After Done, the board shortened the relative ASK-0116 link. Because this card's
plain Acceptance label makes binding include its whole body, the initial completion
check required reconciliation. Comparing the card bodies showed only that repaired
link; WAVE01–WAVE03 and scope are unchanged. With commands quiescent, the checkpoint
was renewed against the actual Done card without changing any requirement.
The first raster check and contact-sheet montage failed because the local
ImageMagick has no configured font inventory. Selecting existing Helvetica rendered
the original SVG; image append produced the contact sheet. A one-off verification
script initially expected top-level candidates from resume-development; the actual
response nests its status. Reading public status corrected the fixture check. No
product correction was needed for these harness/tool issues.

All checks completed. Both task fixture sessions were released, then the task-owned
temporary consumer/registry/media/HTML directory was removed. No server, waiter,
background command or protected candidate is handed off. The coordinator reported
no source writers; this implementer is the sole bounded engineering writer.

WAVE01–WAVE03 are satisfied for this source guidance/example change. Historical
RFC-ASK-0016 and ASK-0116 acceptance are unchanged. Native Windows, offline file-URL
playback and observed installed-skill loading remain unperformed and unclaimed.
No deployment, consumer migration, Faraday/profile/session change, installation,
publication, push or permission change occurred. No required human review remains.

Terminal documentation and scoped board checks at `eea2808d041d04e946561bf6ed9d84702ddc61fe` pass: 16 RFCs, 117 cards, zero violations.
