# Attended review

A portable Python/HTML companion for user-started human acceptance sessions. It shares one durable session between Claude and Codex drivers in a checkout, supports partial decisions without a waiting driver, and retains a pure local HTML fallback. MASK installs data and links; it never starts the controller during installation.

See [SKILL.md](SKILL.md) for the agent workflow and [session contract](references/session-contract.md) for exact JSON and commands. The core runtime has no third-party dependencies, daemon, database, Git mutation, browser-triggered process execution, Bash or WSL requirement.

Use [Tailscale Serve](references/tailscale-serve.md) on the existing tailnet by
default for every session, including review at the source computer. Loopback and
offline are explicit choices or deliberate fallbacks after missing setup. Share
the complete private HTTPS link while useful independent work continues safely.
Read [Driver waiting](references/driver-wait.md) before sharing: when human input
is the only remaining dependency, qualified automatic wait/resume is standard.
A blocking wait parks the coordinator; inspect saved intake at natural work
boundaries instead while busy. Idle waiting needs an awake host and live tool
connection, with explicit manual resume when unavailable.

The session directory is `<checkout>/.mask/attended-review/`. Ignore that generated directory in the consumer. Treat its verdicts as local acceptance records and transfer the relevant evidence to the authoritative issue/RFC records through the driver. Do not commit live host tokens, full incidental logs or unrelated session history.

Run focused public-path tests:

```sh
python -B -m unittest discover -s skills/attended-review/tests -v
```

The implementation combines the existing SRV/sample_studio HTML review and grouped-choice concepts with the approved unified workflow. It is a new portable implementation, not a retained historical packet converter. Historical packet migrations belong outside this package.
