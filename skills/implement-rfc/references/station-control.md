# Managed station control

Use this procedure when a hook reports managed or retired station ownership, or
when the owner requests station status or local takeover. Ordinary unbound local
chats use the selected execution strategy directly. Hooks remain scoped to managed
checkouts and their durable retired endpoints.

## Inspect and resume here

A replacement chat can submit prompts, inspect the recorded ownership and perform
bounded recovery while the old writer is reconciled. Run the helper through the
installed skill, with the exact consumer root:

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

The prompt hook provides recovery context; it does not parse prose into mutation
authority. For guarded replacement tools, use exactly the argument order above.
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
Legacy supervisors and native Windows lack this control and report the owning
terminal's Ctrl+C step. Automatic owner-proxy and group stop are capability-dependent;
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

Local mode permits ordinary new chats. Retired endpoints remain fenced even if the
station registry is removed or its `codex` field becomes null. Managed identity
changes refuse recovery; restore the recorded registry rather than erasing state or
removing locks. Metadata age never removes a lock or retires a writer.

To manage the checkout again, launch an explicit fresh runtime context with the
existing launcher's `--fresh` controls. The new generation retains the old endpoint
revocations. Old chat history stays available; takeover does not archive it.
