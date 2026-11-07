---
name: clang-split-refactor
description: Split oversized C++ source files into responsibility-named header/source pairs without changing behavior, using libclang over the project's compile_commands.json. Use when a C++ file is too large to review or build comfortably, when classes need outlining into declarations plus out-of-line definitions, or when moved code needs correct includes, preprocessor guards and build registration. Clang and CMake (or any compile database) projects only.
---

# Clang Split Refactor

Move code mechanically; decide the design by hand. The bundled tool turns a
reviewed plan into new files whose text comes from exact libclang extents. You
choose what belongs together, name the files and judge the result.

Resolve the launcher against the directory containing this `SKILL.md`:
`<skill>/scripts/clang-split COMMAND ...` (or `python3 -m clang_split` with
`<skill>/scripts` on `PYTHONPATH`). Every command prints JSON. Run
`clang-split doctor` first; it reports the libclang, resource directory and
macOS SDK it found. Set `CLANG_SPLIT_LIBCLANG` or `LLVM_CONFIG` if discovery
picks the wrong LLVM.

## Establish the consumer contract

Read `<consumer>/.mask/skill-config/clang-split-refactor/project.md` when
present. It names the build presets, the formatter, the registration hook and
any spans that must not move. Keep project scripts (manifests, pins, digests,
post-processing) in the consumer; see
[project adapters](references/project-adapters.md).

## Procedure

1. **Two configurations.** Configure the project twice with
   `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`: the normal build and one that flips the
   largest option (for example tests off). Pass the second as `--alt-build` /
   `alt_builds`; references found in either parse are merged. Code under an
   inactive `#if` is invisible to libclang.
2. **Survey.** `clang-split outline SRC --build B` lists top-level entities with
   line spans; `--class-line N` breaks one class down by member kind.
3. **Outline big classes first** when a class body holds the bulk of the file:
   plan the class into its own stem. Its header keeps declarations; bodies move
   to `.cpp`.
4. **Segment.** `clang-split analyze SRC --build B --alt-build B2 -o graph.json`,
   then `clang-split segment graph.json --max-lines 1500 -o segs.json`. Raise
   `--penalty` for fewer, larger files. Read the segments: they are a starting
   point for cohesion, not a design.
5. **Name and plan.** Write `names.json` mapping segment index to a
   responsibility name (equal names merge), then
   `clang-split plan graph.json segs.json names.json --support STEM --base base.json -o plan.json`.
   Edit the plan freely; the [schema](references/plan-schema.md) documents every
   field. Pass `--ceiling 2000`: private helpers land beside their only users,
   so files exceed the segment budget. Re-segment with a smaller `--max-lines`
   until `over_ceiling` is empty; a first guess is
   ceiling × (method lines / total lines) − 150. Free functions segment like
   members and move as `source_only` definitions.
6. **Dry run, then write.** `clang-split extract plan.json` reports notes,
   unresolved includes and per-file sizes. Resolve every note you do not
   understand. Then `clang-split extract plan.json --write`, which also runs the
   plan's registration hook.
7. **Prune** the remaining source: `clang-split prune-includes plan.json --write`.
8. **Format** with the project's formatter.
9. **Gate.** Build *both* configurations, then run the tests. Stop at the first
   failing build: a test run after a failed build exercises stale binaries.
   Read each gate's full output or its exit status; never pipe a gate into
   `tail`/`head`, which replaces the gate's exit status with the pipe's.
   Never regenerate sources while tests run; contract tests and nested builds
   read the tree. Rerun a timing-sensitive failure alone before blaming the
   split.
10. **Review the diff** as a move: every removed line should reappear verbatim
    apart from qualification, declarations and includes.

Make each round reproducible: a script that resets the source and lists,
deletes untracked generated files, extracts, post-processes, formats and
registers. If the base branch moves, rebase the *plan* and regenerate on the new
base; do not hand-merge generated files.

## Rules the tool relies on

These come from splitting a 42k-line file; the reasons are in
[rules](references/rules.md).

- Guard a generated include only with command-line (`-D`) or platform macros,
  and never less than the source guarded the same include.
- A file that tests a macro in `#if` must include the header that defines it.
- Count complete-type needs from member access and implicit conversions, not
  just named references.
- Match anonymous-namespace helpers by text as well, since uses inside templates
  and generic lambdas are often unresolved; overloads move together.
- Deduced-return and `constexpr` functions stay whole in headers (`inline`).
- Leave spans that a security review, digest or contract pins in place: list
  them in no group, or route their bodies to the `__root__` unit and check that
  the old span with one indentation level removed equals the new one.
- Mutable namespace-scope variables moved into a header become `inline`.
- Tests that scan source text (call-site counts, member inventories, temp-dir
  copies of the tree) must learn the split file set.

## Limits

- Clang front end and a compile database only. MSVC-only code, other compilers'
  extensions and non-CMake builds without `compile_commands.json` are untested.
- Only the configured builds are parsed. Branches for other platforms keep their
  text but get no include analysis; build on those platforms before merging.
- Formatting assumes one indentation unit per level and namespace contents
  indented `namespace_indent` levels; run the formatter afterwards.
- Macros that generate declarations, unusual preprocessor layouts and
  definitions split across `#if` branches may need manual post-processing.
- Choosing responsibilities, names and API boundaries stays a human decision.

## Self-test

`python3 -B -m unittest discover -s <skill>/tests -p 'test_*.py' -v` splits the
bundled corpus, builds it in two configurations and compares the program
output. Corpus tests skip, naming the missing tool, without libclang or CMake.
