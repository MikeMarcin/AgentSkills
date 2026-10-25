# Remote station

A portable Python skill that runs one checkout as a persistent remote station: a
named Claude Remote Control session plus a persistent Codex task, held by one
writer lease, with durable identity, status and local takeover. It needs only the
Python standard library, Git, and the Claude and Codex CLIs for a real launch.

See [SKILL.md](SKILL.md) for the agent workflow and the
[station contract](references/station-contract.md) for identity, naming, launch
controls, the lease and transports.

## Consumer setup

1. Install the skill with MASK (`mask install remote-station`, or the `rfc`
   bundle). It is linked at `.agents/skills/remote-station`.
2. Write `.mask/skill-config/remote-station/station.json` (schema in
   [schemas/station-config.schema.json](schemas/station-config.schema.json)) and
   validate it with `scripts/station_config.py`.
3. Optionally install the version-free command once per machine:
   `python3 scripts/install_command.py --bin-dir ~/.local/bin` (any directory you
   put on PATH). Reinstalling from a newer skill version is idempotent and never
   changes station behavior: the command always runs the current checkout's link.
4. Ignore `.remote-station.json` in the consumer; it is machine-local state.

A project wrapper such as `scripts/launch_remote_station.py` should be a few lines
that run `.agents/skills/remote-station/scripts/launch_remote_station.py` with the
same arguments. That path and invocation shape is the skill's frozen entry
contract; later versions may change anything behind it, but not move it.

implement-rfc keeps temporary forwarders at its former
`scripts/launch_remote_station.py` and `scripts/station_control.py` for one
release. They run this skill's scripts when it is installed beside implement-rfc.

## Tests

```sh
python -B -m unittest discover -s skills/remote-station/tests -v
```

The suite covers configuration, the entry contract and both command forwarders
(`cmd` and POSIX `sh`) through disposable consumers, plus the station launcher,
Codex provisioning, lease, lifecycle, takeover, guard and hooks with fake
runtimes. It never starts a real Claude or Codex runtime.
