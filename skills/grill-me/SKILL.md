---
name: grill-me
description: Interview the user to stress-test a plan, decision, or idea through dependent questions and reach explicitly confirmed shared understanding.
---

# Grill me

Interview until the requested scope has a shared understanding. Standalone use is
conversation-only by default, including nonsoftware decisions; create artifacts only
when requested or when an invoking skill owns that artifact workflow.

## Decision tree and frontier

Map the topic as a decision tree: decisions depend on earlier answers and discovered
facts. Recover current scope, settled answers and open questions on resume. A changed
answer reopens dependent branches and affected confirmation; retain unaffected answers.

Investigate discoverable facts yourself with available tools, files or sources.
Exploration is an unsettled prerequisite for questions that depend on it; independent
branches can continue. Delegate only when separately authorized and supported; this
interview never requires subagents. Distinguish observed facts, contradictions,
recommendations and user decisions. Surface conflicting constraints with concrete
scenarios instead of silently rewriting one side.

The **frontier** contains questions whose prerequisites are already settled. Ask up
to three independent frontier questions per round, each with a clear recommendation
and the relevant tradeoff. A question that depends on another unanswered question
belongs to a later round. Prioritize material decisions and the user's requested
focus; do not turn a focused review into a mandatory full design interview.

Use an available question tool when it supports the task, or normal conversation.
For dependent interview decisions, wait for explicit user answers; never set
`autoResolutionMs` or treat elapsed time, silence or a tool's empty response as an
answer. Recommendations remain unaccepted until answered. If an optional-question
tool cannot keep a required answer pending, ask in conversation and stop dependent
work. A partial answer settles only the answered portion; retain other questions
and continue independent investigation without guessing.

## After an answered round

Update settled decisions, rationale and consequences; recompute the tree and frontier.
An artifact-owning caller applies these changes across its authoritative documents,
acceptance, work and milestones and regenerates derived views. Pass the caller the
changed decisions, dependent branches, open questions and coverage; carry scope and
artifact locations without restarting intake. If interrupted, leave a concise
continuation containing the pending questions and answered portions in the existing
conversation or requested record.

For the whole requested scope, finish when all material branches are settled or
explicitly deferred with their consequences understood. An unresolved material choice
is still open; a deferral may leave affected scope unready. Optional internal detail
need not be exhausted when the required behavior is defined. For a focused review,
state the actual branches covered and material questions found elsewhere.

Finish with a concise shared-understanding summary: scope, decisions, tradeoffs,
open questions/deferrals and coverage. Ask for explicit confirmation and wait. Record
confirmation only for the actual summary/version answered; changed decisions reopen
affected confirmation. The caller's original authorization remains intact: this
interview does not authorize publication or implementation, and it adds no gate
to unrelated or independently authorized work.
