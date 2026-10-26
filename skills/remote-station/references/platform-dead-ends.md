# Platform dead ends

Reproduced failures of station launch and Codex provisioning, with the supported
route for each. Read this before changing `launch_remote_station.py` or
`codex_station.py`, and when a station fails on one platform. They were expensive
to discover and are easy to reintroduce. Do not reopen one without evidence that a
newer Codex capability probe changed the underlying product behavior. First
reproduced in AITO (AGD-0057, 2026-08-31); they apply to every consumer.

| Attempt | Observed failure | Supported route |
|---|---|---|
| Run `codex remote-control start` on native Windows. | CLI refuses; the App Server daemon lifecycle is Unix-only. | Native Windows: let Codex Desktop own Remote; use `codex app <checkout>` plus a short-lived standalone stdio helper for task provisioning only. Unix, including WSL2: installer-managed daemon. |
| Start a standalone `codex app-server --listen stdio://` and call `remoteControl/enable` while Codex Desktop is open. | The two Remote owners compete; Remote enters an errored state and normal desktop use is disrupted. | The standalone process may perform thread RPCs only and must close after provisioning. Never call `remoteControl/*` from it. |
| Attach `codex app-server proxy` to the Windows Desktop-owned App Server. | The original probe failed against `app-server-control.sock` with Windows error 10050 (`dead network`). | Provisioning uses standalone stdio. A later CLI 0.153.4 probe passed the SSH WebSocket handshake and a desktop task read through the existing Desktop server; treat that as a host-specific capability, not the launcher's route. |
| Treat `codex app-server proxy` as a JSONL subprocess. | The Unix daemon proxy begins an HTTP WebSocket upgrade, so JSONL requests never form a valid session. | On Unix, perform the WebSocket handshake and exchange masked WebSocket frames over the proxy's stdio. |
| Create and name an empty task, then immediately report it ready. | The task can remain absent from controller task lists. | Run one read-only bootstrap turn, event-wait for `turn/completed`, restore the exact name, verify it, and unsubscribe from the task. |
| Resume an already materialized task merely to verify its name, checkout, or project. | Codex Desktop may already own the task writer, so the short-lived helper is rejected as a second writer. | Use `thread/read`, `thread/metadata/update`, and `thread/name/set` without resuming; acquire a writer only when an empty task needs its bootstrap turn, then unsubscribe. |
| Read a long-lived station task's turns under the default request timeout. | An 87-turn task took 58 seconds under CLI 0.164.0, past the 30-second default, and the relaunch failed. | Turn reads use a history-sized timeout; other requests keep the default. |
| Interrupt empty-task provisioning after `thread/resume`, then relaunch. | The short-lived helper can leave the empty task reporting an active writer. | The bootstrap path calls `thread/unsubscribe`. On relaunch, clear and retry one exact active-writer error only when no recorded turn is active; never clear a writer for an in-progress turn. |
| Create/materialize a second task from inside the already-active Windows station turn and synchronously wait for it. | The host serializes active turns and the experiment deadlocked until the outer turn unwound; a detached helper also produced no controller-visible task. | Provision through the launcher's short-lived local helper before Claude starts; never self-bootstrap from the station task. |
| Reuse a convenient nonempty task or rely on queue `/rename`. | It hijacks unrelated history and does not establish an immutable station binding. | Resolve exact name plus checkout, store the thread ID, and fail closed except for a registry task that is empty or contains only the provisioner's exact completed bootstrap turn with no tool activity. |
| Require a Windows-to-Mac `<codex_delegation>` callback. | The attended cross-host callback was rejected, and the Windows ChatGPT app did not expose **Control Other devices**. | The Mac driver sends the follow-up, holds a bounded `wait_threads` event wait, then reads and validates the Windows task's completed turn. |
| Interpret controller `thread_list_unavailable` as proof the Windows device is disconnected. | The Windows UI can show the device as connected while only the Mac controller's task-catalog operation is unavailable; the API exposes no deeper cause. | Report the operation failure precisely. Provision locally on Windows; defer automated dispatch until controller list/wait/read can resolve the task. |
| Resume Claude with bare `--continue`, or start fresh while recent sibling bridge pointers remain visible, from a linked worktree. | Claude deliberately searches the directory and its Git worktrees, so one worktree's launch can adopt a sibling worktree's newer session even when the launcher supplied its own name. | Persist the exact bridge session in `.remote-station.json` and resume with `--session-id`. For a fresh endpoint, briefly isolate all repository-worktree bridge pointers, start `--name ... --spawn session`, record the new exact-checkout pointer, then restore sibling pointers. |
| Hide this checkout's own bridge pointer for a fresh Claude session, or rely on Ctrl+C to release a terminal Remote Control environment. | A terminal `claude remote-control` preserves its environment on exit. The server then answers a new registration for the same device and folder with 409 "already served by a terminal `claude remote-control`" even though no process is running. Leaving the old pointer in place instead adopts its session. | While isolated, write an environment-only pointer at the checkout path: old `environmentId`, `source`, `pid` and `procStart`, empty `sessionId`. Claude reuses the environment, starts a new session, and still refuses an environment a live server owns. |
| Treat a running station or an accepted cross-session send as delivery. | Replies were held or refused at the receiving dispatcher, whose `crossSessionInbound` setting the station cannot see. | The launcher prints the **Claude return path UNVERIFIED** warning; confirm receipt in the dispatcher before unattended dispatch. |
| Expose App Server on a network port or use `codex --remote` as a task registry. | Adds an unauthenticated protocol surface, or selects by terminal-session state rather than durable station identity. | Keep App Server on local stdio/proxy transport; use persistent task APIs for exact list/send/wait/read routing. |

Native Windows additionally prints an attended placement step when a provisioned
task lands under **Recents**: drag that exact task onto the consumer's Codex
Desktop project. App Server `project/update` and `thread/metadata/update` do not
update Desktop's separate sidebar assignment, and no supported placement RPC is
exposed. On Unix a normal start requires connected Codex Remote status and
`--pair-codex` is the attended path; on native Windows `--pair-codex` refuses and
directs to Desktop's **Control this PC** setup. WSL2 is a separate Linux station
with its own ext4 checkout and Codex installation — never a workaround inside the
native-Windows checkout.

Fixture tests prove none of these platform behaviors: Desktop sidebar placement,
real pairing, Windows controller enumeration and cross-device delivery need an
attended check on the owning host.
