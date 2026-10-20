# Portable mixed audio example

`mixed_audio.py` generates an inline version-2 manifest using six synthetic PCM
tones, one ordinary brief and an intentionally invalid clip. It needs only Python
3.11+; it fetches nothing and does not prepare real assets.

Create a disposable consumer and shared fixture registry outside your source
checkout. Link the canonical `attended-review` package into that consumer's
`.agents/skills/`, then run its helper with that explicit consumer root:

```sh
python /path/to/attended-review/examples/mixed_audio.py --output /tmp/audio-manifest.json
python /path/to/consumer/.agents/skills/attended-review/scripts/attended_review.py --repo-root /path/to/consumer --registry /path/to/fixture-registry init --manifest /tmp/audio-manifest.json
python /path/to/consumer/.agents/skills/attended-review/scripts/attended_review.py --repo-root /path/to/consumer --registry /path/to/fixture-registry prepare
python /path/to/consumer/.agents/skills/attended-review/scripts/attended_review.py --repo-root /path/to/consumer --registry /path/to/fixture-registry serve
```

Open the complete printed loopback URL. Use Launcher A/B/C and Death A/B/C buttons
to compare sequentially. Every clip has its own accept/reject answer; the other
alternatives remain pending. Save a comment before answering, switch and return,
then reload. On Death C, reject for death and add “consider for pain”; this comment
approves no other use. Edit that feedback, clear the answer, and check that the
comment remains. The broken clip must show a load/decode failure without an answer.

For offline review, use `html --output /path/to/review.html` after preparation and
open that file in a browser that allows local HTML/audio. The same page offers
listening, feedback and partial JSON export. Browser storage is a convenience;
import the exported version-2 JSON through `import --file FILE` to make it durable.
A browser that refuses local files has not qualified this offline path. No remote
host or browser-policy change is part of the example.

Use `status --after SEQUENCE` to observe saved feedback and decisions, then
`hand-back` or the page's Finish action to return the partial queue. A normal
`wait --kind handed-back` remains blocked during individual feedback saves.
Stop the fixture host with `stop` before deleting only the disposable consumer.
The tones and fixture verdicts provide no Faraday rights, game or native Windows
qualification and do not migrate a consumer.
