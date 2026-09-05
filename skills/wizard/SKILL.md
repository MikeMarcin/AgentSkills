---
name: wizard
description: Guide required manual steps one at a time with portable local HTML or CLI, durable progress, and agent-captured observations. Use for setup or attended workflows that need human actions without a long checklist.
---

# Wizard

Use this companion for the manual portion of the user's task. Do the mechanical
preparation and observe results with available tools; ask for a human response
only when the action or judgment requires it. Existing task authorization still
applies. Do not add a planning confirmation or a confirmation after every
automatable step.

Write a short JSON definition using the [interface](references/interface.md).
Each step has one instruction, an expected result, and a response type. Use
`observation` for results the agent can capture; use `ack`, `choice`, or `text`
only for an actual human response. Keep secrets out of definitions, responses,
evidence and browser storage. Direct credential entry to the destination app.

Run `scripts/wizard.py init --definition FILE --state STATE_DIR`. Choose a
consumer-local ignored state directory, usually `.mask/sessions/wizard/NAME`.
Both Claude and Codex use these same commands and attach to the same state.
Start `serve --state STATE_DIR --open` for a requested guided session. The
temporary loopback host saves each response immediately; leave it running while
the user works. A second host invocation attaches to that state instead of
starting another host. Other state directories use separate automatic ports.

Use `status --state STATE_DIR` for compact progress. Capture an observable
result with `record --state STATE_DIR --step ID --actor agent --value JSON`.
Never record a human answer inferred from telemetry. A browser cannot run
commands, supply agent observations, mutate Git, or finish RFC cards.

When the user pauses, retain progress without assuming any unanswered result.
Resume through the existing page or `resume`; stop only this host with `stop`.
For server trouble, `html --state STATE_DIR --output FILE` creates a standalone
page. It offers copy/download of **partial** responses for `import`; no full
batch is required. `cli --state STATE_DIR` uses the same definition and durable
intake without a browser. Read the interface only when preparing a definition
or integrating these commands.

For attended-review, the driver creates or resumes the wizard, observes its
completion, and continues the same user request. Keep candidate protection and
human acceptance in attended-review/implement-rfc; wizard completion alone is
not product acceptance.
