# Scoped host controls

Use a task-owned configuration for a newly opened native session. Existing loaded
sessions are not reconfigured by rendering files. Preserve authentication, permissions,
project correctness instructions and global settings. Record the selected surface/build,
requested configuration, effective configuration and actual observations separately.

For direct Codex execution, request the exact primary model/effort and set
`[agents] enabled = false` in supported scoped session configuration. A file alone
proves neither loading nor enforcement. Model invocation through shell/companion tools
is also outside direct policy. Unsupported controls remain explicit limitations.

[Official subagent controls](https://learn.chatgpt.com/docs/agent-configuration/subagents)
and [configuration precedence](https://learn.chatgpt.com/docs/config-file/config-reference)
describe controls, not live qualification. No source check launches a model.

`strategy_host.py render --selection FILE` prints requested Codex TOML to stdout;
place it only in an explicitly task-owned scoped configuration. `inspect` accepts
ordered `--config FILE` layers (low to high precedence), `--instructions FILE` and
`--agent-root DIR` inputs. It reports route/control mismatches, custom agent files,
inherited child defaults and possible coordination directives. `--complete-inputs`
is an operator assertion about supplied layers, not observed host loading. Missing
coverage and heuristic limitations remain visible even when no signal is found.

Native rendering enables native delegation and requests the selected primary route.
It sets no child-route defaults. Existing custom agents or global defaults must be
excluded through supported scoped configuration or isolated task setup; this helper
never deletes them. Rendered files cannot turn this already-loaded session into a
clean native arm. Establish actual behavior during the owner-authorized run; no
separate live qualification is required by the execution-strategies delivery mandate.

Strict planner-worker rendering supplies the exact worker defaults and
`agents.max_concurrent_threads_per_session = 1`. Also pass the exact worker route in
the spawn request. Custom definitions can override it, so inspect inherited agent
files before use. The one-child cap is a session control; the worker's no-delegation
instruction and observed lifecycle still need checking. No custom RFC roles are
required. MASK readiness remains separate from configuration and serving evidence.

The coordinator-implementer default uses the same one-child cap, with Sol Low for
the coordinator and Astra Max for its implementer. `render` prints the coordinator's
scoped settings; `render-implementer` prints the implementer's exact route with
delegation disabled. Use the generic native agent with explicit model/effort and a
fresh context, never an inherited custom RFC role. Other installed RFC role names
are not used by this recipe. A custom definition overriding the selected generic
role still needs reconciliation. Do not change global settings or an active
assignment to apply these task-scoped outputs.
