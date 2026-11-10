# Project adapters

Project policy stays in the consumer repository. A typical adapter is two small
files next to the plans.

## Round script

One command that recreates a round from a clean source, so a plan edit or a
moved base branch means rerunning, not merging:

```sh
#!/bin/sh
set -e
plan=$1
git checkout -- src/widget.cpp CMakeLists.txt     # source and every registered list
git clean -fq -- src/widget_*                      # generated files only
clang-split extract "$plan" --write --report "${plan%.json}.report.json"
[ -f "${plan%.json}.post.py" ] && python3 "${plan%.json}.post.py"
clang-split prune-includes "$plan" --write
tools/format.sh src/widget.cpp src/widget_*
```

A `*.post.py` per plan holds one-off fixes the tool cannot infer (an include a
macro expansion needs, a comment to reword). Keep them short; a growing post
script means the plan should change instead.

## Registration command

When a build also tracks files in manifests or pinned digests, set
`register.command`. Example from a project whose composition contract pins
digests of its source list (shown for shape, not reuse):

```python
"""Register split files and reseal the composition pins."""
import os, re, subprocess
files = os.environ['CLANG_SPLIT_FILES'].split('\n')
# 1. Rewrite the file lists after their anchors (CMakeLists and contract).
# 2. Ask the contract script for the new digests:
out = subprocess.run(['cmake', '-DPRINT_PINNED_DIGESTS=ON', '-P', 'tests/composition_contract.cmake'],
                     capture_output=True, text=True)
pins = dict(re.findall(r'PINNED_DIGEST (\S+) ([0-9a-f]{64})', out.stdout + out.stderr))
# 3. Refuse to move a pin the reviewer must approve; update the others.
```

The refusal matters: a hook that rewrites every pin hides exactly the change
the pin exists to surface.

## Consumer context

`.mask/skill-config/clang-split-refactor/project.md` should state the two build
presets, the formatter command, the round script, the registration hook and any
files or spans that must not move.
