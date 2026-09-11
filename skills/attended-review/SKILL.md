---
name: attended-review
description: Prepare and conduct resumable human review sessions with a local HTML queue, durable partial decisions, scoped candidate protection and an offline fallback. Use when the user requests attended review, preparation for a review session, or a focused burn down of work waiting on human input.
---

# Attended review

Use this companion only for acceptance that actually needs human attention. Ordinary automated verification does not gain a new human checkpoint. `implement-rfc` owns card selection, acceptance judgment and Git operations; this skill owns candidate presentation, preparation and immediate decision intake. The same commands work for Claude and Codex.

1. Select the current repository's human waits through its board tooling. Read only the selected cards and relevant acceptance. Keep repositories independent. Group coupled choices as one candidate; keep independent decisions separate.
2. Write a small manifest using [the contract](references/session-contract.md). Name the actual candidate revision, criteria and relevant paths/resources. Include concise review material or inline media; prefer a prepared stable build. Put mechanical preparation in reviewed argument-array commands or existing repository adapters. Do not put secrets in review content or logs.
3. Run `init --manifest FILE`, then `prepare`. Already available material becomes ready immediately; quick commands run first. Known slow work waits for `prepare --include-slow`, and `--max-items` bounds a batch. A driver may use `ready ID --evidence TEXT` after performing the relevant installation/check itself. Do not equate process exit with human approval.
4. Open `serve`'s complete loopback URL. It is a temporary foreground process started for the user's requested session. Starting another host in the same checkout attaches to the existing one; other checkouts use independent ports. Keep the process available through the driver's ordinary command session. Do not install a daemon. The HTML saves every decision immediately without requiring an active driver. Then, before ending your turn, arm `wait --after SEQUENCE` as a background watch whose exit re-invokes you: on Claude Code that is `Monitor` with `persistent: true`, because a plain background shell command is capped at ten minutes, shorter than a review; Codex uses its equivalent long-lived background command. Without that watch the **Finish and hand back** click is a file nobody reads.
5. Let the user start with ready items while preparation continues, skip, or stop at any time. **Start with what’s ready** interrupts current preparation while preserving ready items. Pause and closing the browser preserve candidate protection. Partial work is useful work; never require draining the whole queue or treat fatigue/skip as rejection.
6. When `wait` returns, or on any resume, read `status --after SEQUENCE` for compact new events; `wait` prints the events it woke on. Capture observable evidence yourself with focused logs, screenshots or repository checks using `observe`; use the wizard companion for truly manual steps. A successful command is objective evidence, never a subjective user verdict. Apply the explicit user verdict only to its recorded candidate. Use the RFC workflow's finish command only when all acceptance is satisfied; the browser never commits or moves cards.
7. Before work that may invalidate a prepared candidate, query `conflicts --paths ... --resources ...`. For the user's explicit **resume development**, release only relevant candidates with `resume-development`. Unanswered affected items need preparation again; other packets/installations remain usable. Already recorded verdicts stay bound to what was reviewed. Relevant changes can require a new candidate revision; unrelated HEAD movement does not.
8. `stop` stops this checkout's host only. It does not release resources or approve pending work. Reopen with `serve` to resume.

Run the script from the installed skill, always selecting the consumer explicitly:

```sh
python /path/to/consumer/.agents/skills/attended-review/scripts/attended_review.py --repo-root /path/to/consumer status
```

Use the supported Python executable on that machine (`python`, `python3` or a known absolute path). The core requires Python 3.11+ and its standard library; native Windows requires no Bash or WSL.

For offline operation, `html --output /path/to/review.html` embeds a complete local page. The user can export any partial decisions with one Copy JSON or Download JSON action. Feed that JSON to `import --file FILE` (or `--file -` for stdin). Offline and server paths share exactly the same intake. No giant Markdown packet or searching for a copy block. Generate the file after preparation; stale or unprepared candidates refuse import. Browser storage is a convenience, not the durable intake: import the export before considering offline decisions recorded.

Only load the [full command and manifest contract](references/session-contract.md) when preparing a session or resolving a concrete issue. No exhaustive product validation or repeated review ceremony is implied by this skill.
