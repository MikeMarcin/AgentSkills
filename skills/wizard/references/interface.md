# Portable wizard interface

Requires Python 3.11+ and its standard library on Windows, macOS or Linux. Native
Windows can use `py -3`; no Bash, WSL, PowerShell script or installed web package
is required. Commands emit one JSON result; interactive CLI prompts go to
stderr. `serve` emits the local URL immediately, then runs in the foreground.
An agent can launch it with its normal persistent process tool. No daemon is
installed. `stop` affects only the host for the supplied state directory.

## Definition

```json
{
  "schema_version": 1,
  "id": "device-check",
  "title": "Prepare the test device",
  "steps": [
    {"id": "connect", "title": "Connect the device",
     "instruction": "Connect the test device and unlock its screen.",
     "expected": "The device appears in the agent's device listing.",
     "response": "observation"},
    {"id": "choose", "title": "Choose the display size",
     "instruction": "Choose the display size you want to inspect.",
     "expected": "A size selected by you.", "response": "choice",
     "options": ["Compact", "Comfortable"]}
  ]
}
```

Required definition fields: `schema_version: 1`, portable `id`, `title`, and
nonempty ordered `steps`. Each step requires unique portable `id`, `title`,
`instruction`, `expected`, and `response`. Optional `url` opens an HTTP(S)
destination using a normal link. Text is displayed literally, never as HTML.
No shell commands, scripts or handlers are accepted in the definition.

| Response | Intake value | Who records it |
|---|---|---|
| `observation` | `{"summary": "Device listed", "evidence": "artifact path or concise result"}` | Agent through CLI |
| `ack` | `true` | Human action that cannot be observed practically |
| `choice` | One exact entry in the step's unique `options` strings | Human |
| `text` | Nonempty non-secret text, up to 8,000 characters | Human |

Steps complete in order. The page can inspect previous/next instructions, but
cannot bypass a pending prerequisite. Pause preserves every answer; resume
continues at the first pending step. There is no automatic verdict for a
skipped or unanswered step. Keep independent procedures in separate wizard
definitions so one wait does not gate unrelated work. Do not introduce steps
whose only purpose is confirming the previous automated action.

## Commands

All commands take an explicit `--state DIR`. Paths are native paths; quote them
for the calling shell when needed. Example commands below omit the interpreter
and the path to `scripts/wizard.py`.

```text
init --definition definition.json --state DIR
status --state DIR
status --state DIR --since 3
record --state DIR --step connect --actor agent --value '{"summary":"Device listed","evidence":"device-list.txt"}'
record --state DIR --step choose --actor human --value '"Compact"'
pause --state DIR
resume --state DIR
serve --state DIR --open
html --state DIR --output wizard.html
import --state DIR --file partial-responses.json
cli --state DIR
stop --state DIR
```

For portable quoting or longer observations, `record --value-file FILE` accepts
a JSON file instead of `--value`. The driver may use `--actor human` only to
transcribe an actual response. Browser/import intake can record only human
responses. Observation steps display a waiting message until the agent records
the measured result. `status --since REVISION` includes compact events after
that revision. Plain status includes counts and the next instruction, not the
full procedure or answer history. Both drivers can read it without consuming
or deleting events.

`init` is idempotent for the exact same definition. Changed definitions require
a new state directory; a completed result remains bound to its original
definition. State writes use an OS file lock and atomic replacement. Competing
answers conflict; an identical repeat is idempotent. Browser updates use an
expected revision to avoid silently overwriting concurrent work. No command
edits a completed answer; make a new wizard for a changed procedure or rerun.

## HTML and offline intake

The live page uses a capability URL and authenticated same-origin requests to
127.0.0.1. It saves each answer to `state.json` before showing success, including
when no agent is running. Keep its local URL private. Host metadata is scoped
to the state directory; ports are selected by the OS. Closing the tab is not
stopping the host. `stop` uses the recorded capability, not a process-name kill.

Standalone HTML is fully usable as a `file:` page. It caches partial progress
in browser storage when available and always supports copying/downloading
partial JSON. Browser storage is only a convenience, not durable driver intake;
save an export before closing if storage is unavailable. The Copy button falls
back to a selected text box when browser clipboard permission is unavailable.
The driver imports that file with the same value validation and identity checks
as live intake. Each export identifies the state and definition and includes
only human responses. Existing agent observations are displayed but cannot be
fabricated through an import. Reopening after agent observations requires a
fresh HTML export. Exported values must not include secrets.

`import --file -` reads JSON from stdin, including a directly supplied pasted
export. Import applies the whole submitted partial set atomically in step order;
it cannot replace earlier answers or apply to another wizard. A stale offline
page may conflict with another driver's answer; preserve the existing result
and regenerate the page. If durable state was paused before the offline session,
the driver runs `resume` before importing its new responses; the export cannot
silently clear a pause made by another driver.

## Attended-review handoff

A driver may reference the wizard from a review candidate using
`{"state": "/absolute/path/to/state", "instructions": "Connect the device"}`
and an optional live URL. This is a driver handoff, not an import dependency
between packages. The driver prepares the definition, presents the URL, captures
objective observations, queries completion, and marks the attended candidate
ready when its actual prerequisites are met. A paused wizard does not release
attended candidate protection or imply a human verdict.

## Provenance

Original Python/HTML implementation. The focused-step UX is inspired by
Matt Pocock's MIT-licensed `matt-skills/skills/engineering/wizard` (2026),
inspected locally for this work. Its Bash template and text are not copied;
provisioning helpers and confirm-every-stage rules are intentionally not
part of this companion.
