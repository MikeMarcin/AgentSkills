---
name: remote-station
description: Launch, resume, inspect or take over a checkout's persistent Claude and Codex remote station; configure its station.json; install the launch_remote_station command. Use for station launch, status, takeover, hooks, an ownership guard message, or a station failing on one platform.
---

# Remote station

A **station** is one project, workstream, branch and checkout in one OS environment,
with one recorded authority, bound to a Claude Remote Control session and a
persistent Codex task. This skill owns station identity, the writer lease,
provisioning, status and takeover. The workflow that dispatches work to a station
owns what it sends and with what authority; for RFC work that is implement-rfc's
remote routing.

## Configure

The consumer checkout holds `.mask/skill-config/remote-station/station.json`:

```json
{
  "schema": "remote-station.config.v1",
  "project": "example",
  "display_name": "Example",
  "origin_repo_name": "Example",
  "session_prefix": "ex",
  "station_registry_doc": "docs/development/remote-stations.md",
  "workstreams": {"main": {"branch": "main"}, "win": {"branch": "windows-lane", "platform": "win"}}
}
```

Check it by running the skill's `scripts/station_config.py` from the checkout (`py -3`
on native Windows). A missing, malformed or unknown-key file refuses every launch
before a runtime starts. Moving from implement-rfc's `project.json`: copy these
keys, set the schema, and drop workstreams whose branches no longer exist.

## Run

The entry script is `.agents/skills/remote-station/scripts/launch_remote_station.py`.
Run it from any directory inside the checkout with `python3`, or `py -3` on native
Windows:

| Command | Effect |
|---|---|
| (no arguments) | Start or resume both runtimes under the writer lease |
| `--fresh [codex\|claude\|both]`, `--no-claude`, `--no-codex` | Reset or skip one runtime; `--help-all` lists the rest |
| `status [--json] [--observe-runtime]` | Ownership, lease and activity facts |
| `takeover [--json] [--confirm-runtime-stopped]` | Transfer to local work; defaults to `--mode local --stop-previous` |
| `hooks [status\|off] [--dry-run]` | Inspect or remove station guard hooks |

Every launch with Claude enabled prints a note that the launcher cannot confirm
Claude replies reach the dispatcher. Confirm receipt in the dispatcher before
unattended dispatch; a running station is not delivery.

The skill's `scripts/install_command.py --bin-dir DIR` writes the version-free
`launch_remote_station` and `launch_remote_station.cmd` into DIR without editing
PATH. The command runs the current checkout's own `.agents/skills/remote-station`
link with the same arguments, stdio and exit status, so each checkout runs its
pinned version. Outside a Git repository it exits 3; without the skill link it
exits 4 and names `mask install remote-station`. It never falls back elsewhere.

## Before you act

- Before launching a new station or changing station code, read the
  [station contract](references/station-contract.md): identity file, naming,
  launch and reset controls, writer lease, transports.
- For status, takeover, hooks or an ownership guard message, read
  [station control](references/station-control.md).
- Before changing provisioning or launch code, or when a station fails on one
  platform, read [platform dead ends](references/platform-dead-ends.md).
- When a Codex or Claude upgrade changes station behavior, read
  [runtime compatibility](references/runtime-compatibility.md).

## Hazards

- Identity is the recorded `station_id`, Codex `thread_id` and Claude `session_id`
  in `.remote-station.json`. Never select a task or session by recency.
- Exactly one driver dispatches a turn at a time; there is no cross-provider mutex.
- A free lease or a removed hook never proves a runtime writer stopped.
- `implement-rfc.*` schema markers and Git-directory file names are frozen so
  existing stations resume; do not rename them.

## Verify

```sh
python -B -m unittest discover -s skills/remote-station/tests -v
```

Fixture tests prove no live pairing, Desktop placement, controller enumeration or
cross-device delivery; those need an attended check on the owning host.
