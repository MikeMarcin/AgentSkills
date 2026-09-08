# Bounded execution

Use direct execution for small or coupled work. Use `scripts/run_slice.py` when
stages are already selected and deterministic. Validation does not authorize an
uploaded order. Review the exact order, permission policy and relevant inputs,
then pass the current digest returned by `validate` to `start --approve-order`.

The command-only interface supports `validate --order FILE`, `start --order FILE
--approve-order DIGEST`, and `--repo-root ROOT status|wait|cancel --run ID`. The
final gate returns `awaiting_integration`. The runner never writes an acceptance
decision or finishes a board card. The existing `issue_board.py finish` consumes
the integrator's separate approval.

Orders are at most 128 KiB and 32 tasks. The executable contract lives in
`slice_model.py`: explicit physical consumer identity and invocation root,
relevant input hashes, frozen routing and permission documents, serial commands,
exact argv, deadlines and exit/artifact/test predicates. A final gate depends on
all preceding tasks. `permissions_ref` points to
`implement-rfc.command-permissions.v1` with `execution: local_unsandboxed` and an
exact `allowed_argv` list. Declarations are not an OS sandbox. Inline evaluated
shell fragments refuse; use a reviewed script. Missing or zero selected tests
fail the predicate. Runtime files live under the selected consumer's ignored
`.mask/generated/implement-rfc/runs` directory, never the installed package.

`slice_runtime.Runtime` provides the native-driver boundary: explicit dispatch
intent, owned thread/turn receipt, bounded partial/final reports, collection,
and integration gate. Report production and execution completion can arrive in
either order. A successful process or a report is not semantic acceptance.
Advisory writer locks are never unlinked to steal ownership. Torn tails are
reported and refuse further mutation; interior corruption refuses. A reused or
uncertain attempt is inspected, never automatically relaunched.

Cancellation signals only owned execution and prevents report-only recovery.
A structured eligible limit can use one preapproved recovery budget only if the
driver enforces that capability. Unsupported recovery remains blocked; retain
partial reports for the integrator. Privacy-safe event projection hashes native
identities and omits report text. Local reports themselves are private artifacts.

## Codex companion

`slice_codex.CodexDriver` inspects generated installed protocol fields, initializes
a stdio app-server connection, checks existing ChatGPT authentication, then starts
its own thread and turn. Packets explicitly name cwd, prompt, model, effort,
approval policy, sandbox and timeout. It does not adopt embedded native subagent
IDs, provision keys or fall back to API billing. Model routes are requested
explicitly; native server behavior still requires observation.

Notification streams deliver item reports and turn completion without model
polling. Permission/authentication requests require native host attention; the
adapter does not answer them. Cancellation uses the exact owned thread and turn.
Codex report-only resumption and native turn-count limits remain unsupported;
wall time is bounded. New driver instances do not adopt unverifiable sessions.
Use direct native execution when this limitation prevents safe continuation.

Protocol reference: [OpenAI app-server documentation](https://learn.chatgpt.com/docs/app-server).
Installed schemas, rather than the online example's spelling or a version number,
determine supported native fields. Native macOS/Windows acceptance is recorded on
the owning cards; fake-driver tests do not qualify another platform.
