# Managed station control

Use this procedure for station status, ownership transfer or hook removal.
Station hooks are inactive by default, including existing hook commands without
flags. Ordinary authorized chats follow repository instructions and the selected
execution strategy. The owner removed automatic hook enforcement on 2026-10-11
because it obstructed ordinary work and MASK recovery.

## Project commands

From the consumer checkout, use its existing station management script:

```sh
python3 scripts/launch_remote_station.py status
python3 scripts/launch_remote_station.py status --observe-runtime --json
python3 scripts/launch_remote_station.py hooks status
python3 scripts/launch_remote_station.py hooks off --dry-run
python3 scripts/launch_remote_station.py hooks off
```

Use `py -3` on Windows. If a project has no wrapper, use the installed skill's
`scripts/launch_remote_station.py` from the consumer root. `hooks off` removes
only implement-rfc station commands from `.codex/hooks.json`, preserving unrelated
hooks and settings. Reload project hooks in the host after removal. Hook inspection
and removal need neither a valid station binding nor working MASK readiness.

Removing hooks does not stop a writer or transfer ownership. Reconcile actual
runtime writers before running conflicting work in their checkout. Status reports
ownership and lease facts; a free lease alone does not prove that runtime stopped.
Use takeover only to transfer work to another endpoint or local mode:

```sh
python3 scripts/launch_remote_station.py takeover --json
```

A direct owner instruction to resume here authorizes the scoped stop and transfer.
The command supplies the consumer root, local mode and previous-owner stop option.
If it reports manual stop steps, observe the listed stops before retrying with
`takeover --confirm-runtime-stopped --json`. That flag records a real human
observation, never a guess based on a stale record.

## Explicit hook enforcement

Blocking hooks require deliberately adding `--enforce` to the guard invocation.
The launcher and MASK setup do not install or enable them. This optional mode
retains endpoint, turn admission and retired-endpoint checks described below;
those hook fences do not exist when enforcement is disabled. Hooks are not a
complete security boundary. Human instructions, supervisor leases, Git and board
validation remain the workflow's authority.

## Continue the current endpoint

Ordinary authorized turns through the recorded Codex task continue under its
expected held supervisor lease. The controller is steering that same writer;
it does not need takeover, retirement, a new chat or Ctrl+C between turns.
Validate the station identity, checkout, lease and each work envelope. Invoke
takeover only when the owner requests transfer to another endpoint or local mode.

Canonical launchers emit `implement-rfc.remote-station.v2`. The exact former
`aito.implement-rfc.remote-station.v2` marker is read-compatible with the same
identity and authority checks. Compatibility changes no registry bytes, endpoint,
generation or lease. Other markers carrying a Codex binding remain refused.

### Delegated tool-output turns with enforcement enabled

Some Codex app versions deliver `send_message_to_thread` as a tool-output item,
which does not invoke UserPromptSubmit. If that route has no prompt admission,
make the first tool an exact request through the installed helper:

```sh
python3 -B "/absolute/consumer/.agents/skills/implement-rfc/scripts/station_task_admission.py" --envelope-base64 BASE64_JSON_ENVELOPE
```

On Windows the exact shape is `py -3 -B "C:\absolute\consumer\.agents\skills\implement-rfc\scripts\station_task_admission.py" --envelope-base64 BASE64_JSON_ENVELOPE`.
Use one ordinary command with the quoted absolute helper path, exactly ordered
arguments and canonical base64 of the UTF-8 JSON remote-task envelope. No shell
prefix, suffix, interpreter `-c`, caller session/turn arguments or envelope file
is accepted. The helper's resolved path must equal both the consumer's installed
helper and the adjacent trusted guard helper; the installed link's exact target
is equivalent. Copied helpers receive no admission authority.

The actual PreToolUse event supplies session and turn identity. The hook checks
the current endpoint, lifecycle, project/origin/branch, expected held supervisor
lease, full envelope, authority, ancestor base and expiry before admission.
Caller identity fields and unknown/duplicate fields are refused. The normal
fenced-envelope UserPromptSubmit path remains available. Independent readiness
tasks may have empty RFC/card arrays.

The request CLI only validates syntax and reports `admission: hook-controlled`;
that output alone is not proof of admission. The hook's additional context names
the actual source event/session/turn. Tools need that exact accepted pair, and
request expiry is checked again on later tools. A second request cannot replace
authority in an already admitted turn. Stop clears current authorization.

Always issue a fresh task ID for each request, including retries after a
partially written request. A receipt under the existing Git guard namespace
retains task use after Stop and rejects replay at this endpoint. Receipts confer
no authority and cannot revive a retired or transferring endpoint. Payloads are
bounded to 16 KiB UTF-8 JSON / 21,848 base64 characters; receipts contain only
bounded identity/digest metadata, with at most 4,096 per endpoint session.
Capacity exhaustion refuses admission and preserves history for supported
recovery; do not delete receipts, seed turn records or relax hooks to continue.

## Inspect and resume here

A replacement chat can inspect ownership and perform recovery while the old writer
is reconciled. The project commands above are preferred. The underlying helper
remains available for older installed launchers, with the explicit consumer root:

```sh
python3 /absolute/consumer/.agents/skills/implement-rfc/scripts/station_control.py status --repo-root /absolute/consumer --json
python3 /absolute/consumer/.agents/skills/implement-rfc/scripts/station_control.py status --repo-root /absolute/consumer --json --observe-runtime
```

Use `py -3` on native Windows. Status reports the endpoint, generation, real OS
supervisor lease, stale holder record, activity and pending recovery. The optional
runtime observation attaches to an existing owner proxy; it starts no daemon,
standalone App Server or model turn. An unavailable proxy, `notLoaded` task, old
metadata or free supervisor lease alone never establishes runtime quiescence.

A direct human instruction such as “resume this work here” authorizes the scoped
stop and transfer. Execute it without asking the owner to repeat that authorization:

```sh
python3 /absolute/consumer/.agents/skills/implement-rfc/scripts/station_control.py takeover --repo-root /absolute/consumer --json --mode local --stop-previous
```

The optional prompt hook provides recovery context; it does not parse prose into
mutation authority. Guarded recovery accepts public launcher commands and helper
flags in any order.
Bounded inspection also permits `git -C ROOT status --short`,
`git -C ROOT diff --no-ext-diff --no-textconv --stat`,
`git -C ROOT log -5 --oneline`, `git -C ROOT rev-parse HEAD`, and `cat` of up to five
regular checkout files of at most 1 MiB each. Shell suffixes, pipelines, substitutions
and interpreter programs are refused. Other mutations wait for local ownership.

## Stop evidence and recovery

The helper fences the recorded endpoints before requesting stops. On supported
managed-owner proxies it validates the exact task and checkout, interrupts recorded
active turns, terminates only terminals returned by the task's complete background
terminal inventory, and waits for idle status, terminal turns, no terminals and no
unreconciled descendant tasks. Unknown or incomplete owner capabilities keep writes
deferred. A standalone App Server cannot release Desktop's owning writer through
`thread/unsubscribe`; this helper never substitutes that call or archives the chat.

New POSIX launcher supervisors have an owner-private loopback stop control. The
lease owner stops its own child process group, waits for group reconciliation and
records the result before releasing the lease. No helper kills a PID taken from a
sidecar. Claude's owned group stop requires that positive supervisor receipt;
untracked detached commands and other runtime writers still need manual observation.
For an actual ownership transfer, legacy supervisors and native Windows lack
this control and report the owning terminal's Ctrl+C step. Automatic owner-proxy and group stop are capability-dependent;
fixture tests do not establish native runtime support on a particular host.

If a stop cannot be proved, follow the returned manual step: open the exact listed
runtime endpoints on their owning host, stop active turns and all terminal/background
commands, and reconcile descendant or detached writers. Stop the supervisor in its
owning terminal if its lease is held. After actually observing those stops, rerun:

```sh
python3 /absolute/consumer/.agents/skills/implement-rfc/scripts/station_control.py takeover --repo-root /absolute/consumer --json --mode local --stop-previous --confirm-runtime-stopped
```

That last flag records a human observation. An instruction to resume authorizes
stopping the owner; it is not itself an observation that the stop succeeded.
Keep inspection available and defer new writes while proof remains unavailable.

## Durable ownership

The checkout's Git directory holds lifecycle generations, retired endpoint IDs,
transfer state and stop receipts. The backward-compatible `.remote-station.json`
retains its identity and history. The helper changes neither repository files,
dirty edits, branch, checkpoints, selected strategy nor pending acceptance. It
serializes transfers and launch publication with an OS lock, then acquires the
supervisor lease before publishing local ownership. Repeated takeover is idempotent;
interrupted transfers reuse their durable receipts and original obligations.

With enforcement enabled, local mode permits ordinary new chats. Retired endpoints remain fenced even if the
station registry is removed or its `codex` field becomes null. Managed identity
changes refuse recovery; restore the recorded registry rather than erasing state or
removing locks. Metadata age never removes a lock or retires a writer.

To manage the checkout again, launch an explicit fresh runtime context with the
existing launcher's `--fresh` controls. The new generation retains the old endpoint
revocations. Old chat history stays available; takeover does not archive it.
