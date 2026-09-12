# Disposable qualification guard

Invoke the public helper through the selected consumer's installed skill link:

```sh
python3 /fixture/consumer/.agents/skills/implement-rfc/scripts/qualification_guard.py \
  --allowed-root /fixture/consumer --target-root /fixture/consumer \
  --live-root /real/consumer --live-file /real/consumer/.mask.json \
  --live-file /real/consumer/.mask/skill-config/implement-rfc/project.json \
  -- python3 /fixture/course.py
```

All paths must be absolute. Repeat allowed roots, live roots and live files as
needed. Declare every live consumer root that the course must preserve and each
relevant declaration explicitly; nothing is inferred from the shared skill link.
Existing resolved disposable and live roots must not overlap in either direction.
The selected existing target must resolve inside an allowed root, including through
symlinked parents. Live files must resolve inside declared live roots and be regular
files or missing. Invalid scope refuses before launching the command.

The wrapper sets the command's working directory and `QUALIFICATION_TARGET_ROOT`
to the resolved target. Pass that target explicitly to mutation-capable tools;
review the course's other arguments and environment before running it. The wrapper
compares exact selected bytes (including missing-file state) after synchronous
command completion, even on failure. JSON stdout records before/after existence
and SHA-256 receipts without declaration contents; command output goes to stderr.
Exit codes: 0 passed, 2 refused, 3 live drift, 4 command failed. Preserve the receipt
in the existing qualification evidence. Drift takes precedence over command failure.

This is a cooperative guard, not a process sandbox: it cannot restrict arbitrary
command arguments, subprocesses, races, transient changes restored before checking,
or undeclared files. Do not launch detached writers. Declare disposable roots
narrowly; the helper cannot prove that an operator-labelled root is disposable.
Interrupted/killed guard processes may lack a final receipt; that is incomplete
evidence. It never repairs or restores live files automatically.

For a whole native agent course, the assignment itself must explicitly name the
allowed fixture roots and prohibit writes elsewhere. A wrapper around one helper
does not constrain a native agent or arbitrary child writes. Capture real consumer
declarations and selected native-role lock files before the **entire** course and
compare after every course writer has stopped, including failed courses.

The stdlib module also exposes `capture_live(live_roots, live_files)` and
`check_live(before)` for a supervising Python caller that remains alive across
native interaction. Add the installed skill's `scripts` directory to that caller's
module path, then use this pattern (paths are absolute, explicitly selected):

```python
from qualification_guard import capture_live, check_live
before = capture_live(real_consumer_roots, declaration_and_role_lock_paths)
try:
    conduct_native_course_with_explicit_fixture_assignment()
finally:
    changed = check_live(before)
    # Persist this result in the existing course evidence, even if the course failed.
    record_course_comparison(changed)
```

The two course/record functions above are caller-owned integration points, not
provided APIs. `before` is an immutable `LiveSnapshot` retaining resolved declared live roots,
selected paths, exact bytes and missing-file states in memory. Pass it unchanged to
`check_live`, which rechecks resolved containment and returns changed, escaped or
unreadable paths. An empty list means unchanged within the captured live scope.
This API does not launch, scope or stop agents. If its caller is lost, the missing
comparison remains unresolved evidence; do not recapture and call it the original
baseline. The command wrapper remains the fixture subprocess scope check.
