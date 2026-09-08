# Bounded execution

Use direct execution for small or coupled work. Use `scripts/run_slice.py` when
stages are already selected and deterministic. Validation does not authorize an
uploaded order. Review the exact order, permission policy and relevant inputs,
then pass the current digest returned by `validate` to `start --approve-order`.

The public interface supports `validate --order FILE`, `start --order FILE
--approve-order DIGEST`, and `--repo-root ROOT status|wait|cancel --run ID`. The
final gate returns `awaiting_integration`. The runner never writes an acceptance
decision or finishes a board card. The existing `issue_board.py finish` consumes
the integrator's separate approval.

Orders are at most 128 KiB and 32 tasks. The executable contract lives in
`slice_model.py`: explicit physical consumer identity and invocation root,
relevant input hashes, frozen routing and permission documents, serial commands,
exact argv, deadlines and exit/artifact/test predicates. It also accepts up to
two explicitly approved read-only agent stages in total per order
(`max_agent_dispatches`); other agent roles refuse. A final gate depends on
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

## Claude companion

`slice_claude.ClaudeDriver` capability-checks installed print/stream flags and
requires existing first-party claude.ai authentication. Its explicit packets use
read-only leaf tools (`Read`, `Grep`, `Glob`), a model/effort, native max-turns
request and wall deadline. This companion implementation supports investigation, not
source-writing workers. Safe mode disables customizations while preserving native
authentication and permissions; MCP tools are denied and permission mode is
`dontAsk`. It never uses bare mode, API keys or permission bypass. Managed host
policy still applies. These companion restrictions are explicit and do not
rewrite interactive settings.

The assigned session UUID is native; turn identifiers are labelled logical
assignment IDs because this stream does not expose a qualified native turn ID.
Only structured result subtypes establish completion/limit/failure. Text quoting
a turn limit is a partial report, never proof of termination. The lower-level, fixture-qualified report-only resume interface
uses the exact owned session with all built-in tools disabled and MCP denied,
one turn and the preapproved deadline. Cancellation disables resumption. Native
embedded Agent sessions are not adopted.

Reference: [Claude print-mode documentation](https://code.claude.com/docs/en/headless)
and [CLI flags](https://code.claude.com/docs/en/cli-reference). Installed native
smoke evidence lives on ASK-0034; fixture recovery is distinguished from live
recovery qualification.

## Admitted read-only agent stages

An `agent` stage replaces argv/predicate with `route` and `task_packet`.
The route contains exact provider, role, profile, model, effort and
`permission_policy: read-only-leaf`; allowed roles are utility, scout and the two
reviewers. List the same exact route in the frozen permission document's
`allowed_agents` array. The JSON task packet is a frozen repository input and
uses the native packet fields above, with the same cwd, model, effort and deadline
as the stage. Codex requires `read-only`/`never`; Claude uses its read-only tools.
Set an explicit `max_agent_dispatches` (0–2), empty owned paths and `retry: never`.

The runner collects reports durably and stops at the integrator. Cancellation is
serviced by the owning process during native idle waits; another CLI process only
writes its request marker. If the owner crashes, retained native identity is an
inspection target, not authorization to attach an unverifiable replacement.
Claude session identity is persisted before spawn; Codex thread identity before
turn start and turn identity before the final dispatch receipt. The uncertain
turn-start response window remains explicit and is never automatically retried.

Public report-only recovery and source-writing companion stages remain unsupported.
The lower-level recovery interface is fixture-qualified; it does not establish a
native platform claim. Interactive adapters retain their own report compatibility.
Codex companion leaf restrictions are policy-only until actual available tools
are observed; the read-only filesystem sandbox does not prove tool-level isolation.

Selected usage captures include hashed runtime lifecycle observations in
`runtime_events.jsonl`, with separate coverage. Orders and report text are excluded.
Inclusive native usage aggregates are marked non-additive and never substitute
for reconciled request usage or explicit semantic outcomes.


## Observed Windows limitation

Native Windows qualification with Codex CLI 0.153.4 exercised authentication and
report delivery, but the companion reported command-tool startup timeouts for its
file reads. Its report was collected; the requested inventory was not completed.
Do not claim Windows Codex local-tool execution is qualified from transport
success. Use direct command execution or an explicitly selected qualified runtime.
Windows Claude read-only inventory and report collection were observed with
Claude Code 2.1.263. These are recorded versions, not version-only capability gates.
