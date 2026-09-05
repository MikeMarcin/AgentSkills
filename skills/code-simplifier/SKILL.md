---
name: code-simplifier
description: Simplify, refactor, and polish code for clarity, consistency, and maintainability while preserving behavior. Use when explicitly asked to simplify or clean up code, after implementing code changes that need a refinement pass, when recently touched code has avoidable nesting, duplication, cleverness, stale comments, or inconsistent local style, or when a review asks for maintainability improvements without changing functionality. Focus on recently modified code by default unless the user requests a broader pass.
---

# Code Simplifier

## Core Rule

Preserve behavior. Change how the code is expressed, not what it does, unless the user explicitly asks for a behavior change.

Prefer readable, explicit code over clever or overly compact code. Do not treat fewer lines as the goal.

## Workflow

1. Establish scope.
   - Inspect the user's request, `git status`, and relevant diffs.
   - Focus on files or sections changed in the current session by default.
   - Expand scope only when the user asks, or when a nearby simplification is required to keep the touched code coherent.

2. Learn local standards.
   - Read nearby code before editing.
   - Follow repository guidance such as `AGENTS.md`, `CLAUDE.md`, README files, formatter settings, lint rules, and existing tests when present.
   - Prefer the project's existing idioms over generic preferences. Do not impose language-specific rules from another ecosystem unless they match the repo.

3. Simplify for clarity.
   - Reduce unnecessary nesting with early returns, guard clauses, or extracted helpers when they make flow easier to follow.
   - Remove redundant branches, dead code, unnecessary wrappers, and duplicated logic.
   - Rename unclear local variables or helpers when the new name improves intent without broad churn.
   - Consolidate related logic when it reduces mental overhead.
   - Split functions or components when separate concerns are being mixed.
   - Remove comments that only restate obvious code; keep or add comments for non-obvious constraints, invariants, or tradeoffs.
   - Avoid nested ternaries and dense one-liners when an `if`, `switch`, match expression, or named helper reads better.

4. Keep useful structure.
   - Preserve abstractions that encode domain concepts, isolate side effects, or support testing.
   - Avoid broad rewrites, public API changes, file moves, dependency changes, schema changes, or formatting-only churn unless the user requested them or they are necessary.
   - Keep error handling, logging, telemetry, accessibility, localization, and security behavior intact.

5. Verify.
   - Run the narrowest meaningful tests, type checks, formatter, linter, or build command available for the touched code.
   - If no practical verification exists, inspect the diff carefully and state the residual risk.
   - Compare before and after behavior-sensitive paths, especially edge cases, error paths, async/concurrency behavior, state mutation, and serialization.

## Editing Heuristics

- Prefer one clear concept per function, component, or module boundary.
- Prefer names that describe role or intent, not implementation trivia.
- Prefer local changes over architecture changes.
- Prefer straightforward data flow over hidden mutation or implicit coupling.
- Prefer standard library or established project helpers over new ad hoc utilities.
- Preserve tests unless they are outdated by an intentional user-requested behavior change.

## Final Response

Report the simplification at a behavioral level, mention any verification run, and call out anything deliberately left unchanged because changing it would alter behavior or exceed scope.
