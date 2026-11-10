# Plan schema

A plan is one JSON object. Relative paths resolve against the directory
containing the plan file. `clang-split plan` writes the `groups`; copy the other
fields from a base file with `--base`.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `source` | path | required | File to split. |
| `build` | path | required | Build directory containing `compile_commands.json`. |
| `alt_builds` | paths | `[]` | Other configurations; their references are merged and their `-D` macros may guard includes. |
| `project_root` | path | git root of `source` | Only files under it become quoted project includes. |
| `exclude_dirs` | paths | `[]` | Root-relative directories never included as project headers (vendored code). Build directories are always excluded. |
| `closures` | path | `<build>/clang_split_closures.json` | Cache of which files each candidate include brings in. Delete it when includes change. |
| `subdir` | string | `""` | New files go to `<source dir>/<subdir>/`; includes are spelled `"<subdir>/<stem>.hpp"`. |
| `namespace` | string | enclosing namespace of the first entity | Namespace wrapping generated content; `""` for none. |
| `namespace_indent` | int | `1` | Indentation levels of namespace contents. |
| `indent` | string or int | `"\t"` | One indentation level; an int means that many spaces. |
| `guard_prefix` | string | `""` | Prefix of generated include guards: `<prefix><SUBDIR_STEM_HPP>`. |
| `guard_style` | string | `"name"` | `"path"` spells guards from the header's repository path (`<prefix>SRC_X_STEM_HPP`); `"name"` from `subdir/stem.hpp`. |
| `guard_macros` | strings | `[]` | Extra macros allowed to guard generated includes, beyond platform and `-D` macros. |
| `qualify` | object | `{}` | Name → qualified name substitutions applied to generated text, for names a `using` made unqualified in the source. |
| `source_includes` | bool | `true` | Add each new header to the remaining source; prune removes unused ones. |
| `keep_includes` | strings | `[]` | Includes `prune-includes` never drops, spelled as written (`"<windows.h>"`). |
| `platform_macros` | strings | `[]` | Extra macros whose guarded includes `prune-includes` keeps. |
| `support_doc` | string | `""` | Header comment for the `--support` group. |
| `register` | object | none | Registration hook, run after `extract --write`. |
| `groups` | array | required | One entry per stem, below. |

## Groups

Entity names are the keys `clang-split analyze` prints: the spelling, or
`name@line` for a repeated spelling (overloads, reopened namespaces).

| Field | Meaning |
|---|---|
| `stem` | File stem; produces `<stem>.hpp` and `<stem>.cpp`. |
| `entities` | Moved with declarations in the header: classes are outlined, free functions split into declaration and definition. |
| `private` | Moved into the `.cpp`'s anonymous namespace. |
| `source_only` | Already out-of-line definitions; moved to the `.cpp` only. |
| `header` | `false` writes no header (a pure definitions file). |
| `doc` | Comment placed before the header's namespace. |
| `method_files` | `{unit: [method, ...]}` routes outlined bodies to `<unit>.cpp` instead of `<stem>.cpp`; `"__root__"` keeps them in the source. |
| `default_unit` | Unit for unrouted bodies (default: the stem). |
| `hoist`, `hoist_stem`, `hoist_doc` | Nested records lifted to namespace scope into `<hoist_stem>.hpp`. |
| `comments_follow_definitions` | Move a member's leading comment to its out-of-line definition. |

## Register hook

Default: insert generated files after an anchor line.

```json
{"dir": "src", "prefix": "widget_",
 "lists": [{"file": "CMakeLists.txt", "anchor": "src/widget.cpp",
            "entry": "src/{name}", "kinds": [".cpp"]}]}
```

`dir`/`prefix` select the generated files (root-relative). Each list must contain
`anchor` exactly once; previous generated entries right after it are replaced.
Choose a `prefix` that only generated files share.

Project hook: `{"dir": ..., "prefix": ..., "command": "python3 tools/register_split.py"}`
runs from the project root with `CLANG_SPLIT_FILES` set to the new files. Use it
for manifests, contract lists or pinned digests. `clang-split register ROOT SPEC`
runs either hook alone.

## Report

`extract` prints `notes` (constexpr or deduced-return functions kept in headers,
leading return types to check, references to entities that stay in the source,
unresolved includes), `files` (line counts per header and source),
`std_fallback` (standard names with no canonical header mapping; add an include
by hand if the build needs one) and `register`.
