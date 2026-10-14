# Contributing to AgentSkills

Use the live RFC and local issue-board contracts. The implement-rfc skill automates this process, but human contributors can satisfy the same requirements without a particular agent. Read root/nested instructions, claim a bounded card, implement only owned paths, run focused acceptance checks, keep docs truthful, and commit explicit paths.

Do not treat a detailed RFC packet as completed work. Record actual baseline/integration commits and leave unavailable native-platform cards open. No mandatory broad test matrix or model/runtime subscription is implied. Tests use disposable local fixtures; live private source/auth changes require explicit scope.

Use existing Git authentication and avoid adding credentials to skills, config, output or logs. Public projects must keep their contributor contract readable without access to private skill content.

When changing shared skill content, edit the canonical AgentSkills source through ordinary Git, not a per-project copy. MASK deploys links and has no automatic commit/push or writeback synchronization. Bootstrap and retired-copy provenance remain in `docs/development/`; active deployment uses MASK.

## Local checks

Use Python 3.11 or newer and Git. Set up test dependencies in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -B scripts/verify_documentation.py --root .
.venv/bin/python -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only
.venv/bin/python -B scripts/run_tests.py
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.
The dependency file supplies jsonschema and Pillow for schema and image fixtures.
The test driver requires jsonschema so schema validation cannot disappear behind
dependency skips. Native platform tests still skip where the platform is unavailable.
These checks launch no models and use disposable fixture roots.

To include the actual public MASK command paths, clone ManageAgentSkills using
your existing repository access, then select that local checkout explicitly:

```sh
.venv/bin/python -B scripts/run_tests.py --mask-program /absolute/path/to/ManageAgentSkills
.venv/bin/python -B scripts/verify_mask_examples.py --mask-program /absolute/path/to/ManageAgentSkills
.venv/bin/python -B scripts/verify_rfc_bundle.py --mask-program /absolute/path/to/ManageAgentSkills
.venv/bin/python -B scripts/verify_selected_skill_imports.py --mask-program /absolute/path/to/ManageAgentSkills
```

The bundle/import checks bind a committed source revision, defaulting to HEAD;
commit the candidate first or pass `--source-revision COMMIT`. They use local bare
remotes and temporary consumers, leaving your real registry and personal links alone.

[CI](.github/workflows/checks.yml) always checks portable source, documentation and
offline tests on Linux/Python 3.11. While AgentSkills is private, companion checks
run locally because the job token cannot read another private repository. Public
runs require the public MASK checkout and integration checks; a failed checkout
fails the job. Native driver qualification and human decisions remain separate
from fixture and CI results; see the [preview scope](docs/development/public-preview.md).
