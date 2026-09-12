from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import shutil
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
RENDERER = SKILL_DIR / "scripts" / "render_runtime_adapters.py"
VALIDATOR = SKILL_DIR / "scripts" / "validate_portable_agents.py"
ROUTING = json.loads((SKILL_DIR / "config" / "routing.json").read_text(encoding="utf-8"))
from project_fixtures import init_repo, write_context, CONFIG
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import project_config
PROJECT = project_config.load(repo_root=os.environ["IMPLEMENT_RFC_PROJECT_ROOT"]) if os.environ.get("IMPLEMENT_RFC_PROJECT_ROOT") else CONFIG

VALIDATOR_SPEC = importlib.util.spec_from_file_location("validate_portable_agents", VALIDATOR)
if VALIDATOR_SPEC is None or VALIDATOR_SPEC.loader is None:
    raise RuntimeError(f"could not load portable-agent validator at {VALIDATOR}")
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


class RenderRuntimeAdaptersTests(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        self.mask_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.mask_temp.cleanup)
        self.mask_stub = Path(self.mask_temp.name) / 'mask.py'
        self.set_mask_paths('.mask/generated/{skill}/native-roles.lock.json',
                            ['.mask/skill-config/{skill}/native-roles.lock.json'])
        self.environment = patch.dict(os.environ, MASK_PROGRAM=str(self.mask_stub))
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def set_mask_paths(self, canonical, retired):
        value = dict(data=dict(workflow=dict(paths=dict(native_role_lock=canonical, retired_native_role_locks=retired))))
        self.mask_stub.write_text('import json, sys\nassert sys.argv[1:] == ["capabilities", "--json"]\nprint(' + repr(json.dumps(value)) + ')\n')

    def run_renderer(self, repo_root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        if not (repo_root / ".git").exists():
            init_repo(repo_root)
            write_context(repo_root, config=PROJECT)
        return subprocess.run(
            [sys.executable, str(RENDERER), "--repo-root", str(repo_root), *extra],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def expected_route(self, role: str, provider: str) -> dict[str, object]:
        model_class = ROUTING["assignments"][role]
        return ROUTING["providers"][provider]["classes"][model_class]

    def expected_banner(self, role: str, provider: str) -> str:
        route = self.expected_route(role, provider)
        effort = route["effort"] if route["effort"] is not None else "none (unsupported)"
        return f"Role: {role} | Model: {route['model']} | Effort: {effort}"

    def test_renders_deterministic_native_agents_from_shared_assignments(self) -> None:
        # Approved role assignments are an independent expectation, not derived
        # from the routing file whose accidental edits this test should catch.
        expected = {
            "rfc-integrator": ("gpt-5.6-sol", "xhigh", "claude-opus-5", "xhigh", "workspace-write", True),
            "rfc-utility": ("gpt-5.6-luna", "xhigh", "claude-haiku-4-5", None, "read-only", False),
            "rfc-test-runner": ("gpt-5.6-luna", "xhigh", "claude-haiku-4-5", None, "build-write", False),
            "rfc-scout": ("gpt-5.6-sol", "low", "claude-opus-5", "low", "read-only", False),
            "rfc-worker": ("gpt-6-astra", "low", "claude-opus-5", "xhigh", "workspace-write", False),
            "rfc-worker-deep": ("gpt-6-astra", "high", "claude-fable-5-1", "high", "workspace-write", False),
            "rfc-reviewer": ("gpt-6-astra", "medium", "claude-fable-5-1", "medium", "read-only", False),
            "rfc-reviewer-critical": ("gpt-6-astra", "xhigh", "claude-fable-5-1", "high", "read-only", False),
        }
        self.assertEqual(set(ROUTING["assignments"]), set(expected))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.run_renderer(root)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("rendered 17 files", first.stdout)

            for role, (model, effort, claude_model, claude_effort, mutation, nested) in expected.items():
                with self.subTest(role=role):
                    codex = tomllib.loads((root / f".codex/agents/{role}.toml").read_text())
                    self.assertEqual(codex["name"], role)
                    self.assertEqual(codex["model"], model)
                    self.assertEqual(codex["model_reasoning_effort"], effort)
                    sandbox = "read-only" if mutation == "read-only" else "workspace-write"
                    self.assertEqual(codex["sandbox_mode"], sandbox)
                    self.assertEqual(codex["agents"]["enabled"], nested)
                    instructions = codex["developer_instructions"]
                    self.assertTrue(instructions.startswith("Before any analysis or tool call"))
                    self.assertIn(self.expected_banner(role, "codex"), instructions)
                    self.assertEqual("Delegate only to these leaf roles:" in instructions, nested)

                    claude = (root / f".claude/agents/{role}.md").read_text()
                    frontmatter = claude.split("---", 2)[1].strip().splitlines()
                    header = dict(line.split(": ", 1) for line in frontmatter)
                    self.assertEqual(header["name"], role)
                    self.assertEqual(json.loads(header["model"]), claude_model)
                    self.assertEqual(header.get("effort"), claude_effort)
                    permission = None if role == "rfc-integrator" else ("plan" if mutation == "read-only" else "acceptEdits")
                    self.assertEqual(header.get("permissionMode"), permission)
                    configured = VALIDATOR_MODULE.renderer.load_json(SKILL_DIR / "config/roles.json")["roles"][role]
                    tools = set(header["tools"].split(", "))
                    expected_tools = {"Read", "Grep", "Glob", "Bash"}
                    if mutation == "workspace-write":
                        expected_tools.update({"Edit", "Write", "Skill"})
                    if nested:
                        expected_tools.add("Agent(" + ",".join(configured["delegation"]["allowed_roles"]) + ")")
                        expected_tools.update(VALIDATOR_MODULE.renderer.COORDINATION_TOOLS)
                    self.assertEqual(tools, expected_tools)
                    turns = configured.get("max_turns")
                    self.assertEqual(header.get("maxTurns"), None if turns is None else str(turns))
                    self.assertEqual(turns is None, role == "rfc-integrator")
                    body = claude.split(f"# {role}\n\n", 1)[1]
                    self.assertTrue(body.startswith("- Before any analysis or tool call"))
                    self.assertIn(self.expected_banner(role, "claude"), body)

            for provider, extension in (("codex", "toml"), ("claude", "md")):
                for output_root in (root, SKILL_DIR.parents[2]):
                    self.assertFalse((output_root / f".{provider}/agents/rfc-verifier.{extension}").exists())

            self.assertFalse((root / ".claude/skills/implement-rfc/SKILL.md").exists())
            manifest = json.loads((root / ".mask/generated/implement-rfc/runtime-adapters.json").read_text())
            self.assertEqual(manifest["schema"], "implement-rfc.runtime-adapters.v1")
            self.assertEqual(manifest["assignments"], ROUTING["assignments"])
            self.assertEqual(len(manifest["files"]), 16)
            self.assertEqual(manifest["project"], PROJECT["project"])

            for worker in ("rfc-worker", "rfc-worker-deep"):
                claude_worker = (root / f".claude/agents/{worker}.md").read_text()
                codex_worker = tomllib.loads((root / f".codex/agents/{worker}.toml").read_text())
                for content in (claude_worker, codex_worker["developer_instructions"]):
                    for addendum in PROJECT["role_addenda"].get("rfc-worker", []):
                        self.assertIn(addendum, content)
                    for addendum in PROJECT["role_addenda"].get(worker, []):
                        self.assertIn(addendum, content)
                    attended = PROJECT["attended_review_skill"]
                    if attended is None:
                        self.assertIn("record the pending checkpoint and its exact ask", content)
                    else:
                        self.assertIn(f".agents/skills/{attended}/SKILL.md", content)
                    self.assertNotIn("{attended_review_skill}", content)

            check = self.run_renderer(root, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_candidate_override_is_applied_without_changing_role_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            override = root / "routing.candidate.json"
            override.write_text(
                json.dumps(
                    {
                        "providers": {
                            "codex": {"classes": {"balanced": {"model": "candidate-codex", "effort": "low"}}},
                            "claude": {"classes": {"balanced": {"model": "claude-candidate", "effort": "low"}}},
                        }
                    }
                ),
                encoding="utf-8",
            )
            caps = root / "caps.json"
            caps.write_text(json.dumps({"codex": {"candidate-codex": ["low"]}, "claude": {"claude-candidate": ["low"]}}))
            rendered = self.run_renderer(root, "--routing-override", str(override), "--capabilities", str(caps))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            scout = tomllib.loads((root / ".codex/agents/rfc-scout.toml").read_text())
            self.assertEqual(scout["model"], "candidate-codex")
            self.assertIn(
                "Role: rfc-scout | Model: candidate-codex | Effort: low",
                scout["developer_instructions"],
            )
            claude_scout = (root / ".claude/agents/rfc-scout.md").read_text()
            self.assertIn('model: "claude-candidate"', claude_scout)
            self.assertIn(
                "Role: rfc-scout | Model: claude-candidate | Effort: low",
                claude_scout,
            )
            self.assertIn("Do not edit files", claude_scout)

    def test_check_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rendered = self.run_renderer(root)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            path = root / ".codex/agents/rfc-worker.toml"
            path.write_text(path.read_text() + "# drift\n", encoding="utf-8")
            check = self.run_renderer(root, "--check")
            self.assertEqual(check.returncode, 1)
            self.assertIn("stale generated file", check.stderr)

    def test_compare_reports_portable_differences(self) -> None:
        ours = {"SKILL.md": "a", "scripts/x.py": "b", "README.md": "c"}
        theirs = {"SKILL.md": "a", "scripts/x.py": "changed", "tests/t.py": "d"}
        findings = VALIDATOR_MODULE.compare_manifests(ours, theirs)
        self.assertEqual(
            findings,
            ["only here: README.md", "differs: scripts/x.py", "only there: tests/t.py"],
        )
        self.assertEqual(VALIDATOR_MODULE.compare_manifests(ours, dict(ours)), [])

    def test_portable_skill_and_role_sources_do_not_pin_vendor_models(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        roles = (SKILL_DIR / "config" / "roles.json").read_text(encoding="utf-8")
        for source in (skill, roles):
            self.assertNotIn("gpt-5.", source)
            self.assertNotIn("claude-opus", source)
            self.assertNotIn("claude-sonnet", source)
            self.assertNotIn("claude-haiku", source)

    def test_portable_sources_name_no_project(self):
        renderer = VALIDATOR_MODULE.renderer
        identities = ["Better" + "PullReview", "MASK", "AgentSkills"]
        for path in renderer.portable_files(SKILL_DIR):
            findings = renderer.coupling_findings(path.relative_to(SKILL_DIR), path.read_text(), identities)
            self.assertEqual(findings, [], str(path))
        for text in ('mask = secrets.token_bytes(4)', 'https://agentskills.io/specification'):
            self.assertEqual(renderer.coupling_findings(Path('scripts/protocol.py'), text, identities), [])
        for text in ('display_name: MASK', '"origin_repo_name": "AgentSkills"',
                     'Follow Better' + 'PullReview architecture', 'https://github.com/example/AgentSkills.git'):
            self.assertTrue(renderer.coupling_findings(Path('SKILL.md'), text, identities), text)

    def test_portable_policy_requires_role_names_and_startup_banners(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        delegation = (SKILL_DIR / "references" / "delegated-execution.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("rfc_scout_backend_selection", delegation)
        self.assertIn("rfc_utility_cache_inventory", delegation)
        self.assertIn("Role: <role> | Model: <model> | Effort: <effort>", delegation)


    def test_two_shared_consumers_are_distinct_and_source_immutable(self):
        renderer = VALIDATOR_MODULE.renderer
        before = {str(p.relative_to(SKILL_DIR)): p.read_bytes() for p in SKILL_DIR.rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as temp:
            for name in ('mask', 'agent-skills'):
                root = Path(temp) / name
                init_repo(root, token=name)
                facts = write_context(root, token=name)
                facts['role_addenda'] = {'rfc-worker': [f'Only {name} project rules.']}
                write_context(root, config=facts)
                for target in ('.agents', '.claude'):
                    entry = root / target / 'skills/implement-rfc'
                    entry.parent.mkdir(parents=True)
                    entry.symlink_to(SKILL_DIR, target_is_directory=True)
                result = self.run_renderer(root)
                self.assertEqual(result.returncode, 0, result.stderr)
                for family, suffix in (('codex', 'toml'), ('claude', 'md')):
                    content = (root / f'.{family}/agents/rfc-worker.{suffix}').read_text()
                    self.assertIn(f'Only {name} project rules.', content)
                check = subprocess.run([sys.executable, str(VALIDATOR), '--repo-root', str(root)], capture_output=True, text=True)
                self.assertEqual(check.returncode, 0, check.stderr)
        after = {str(p.relative_to(SKILL_DIR)): p.read_bytes() for p in SKILL_DIR.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_unsafe_destinations_refuse_before_any_write(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            for kind in ('parent', 'leaf', 'unknown', 'marker_without_manifest'):
                root = base / kind
                init_repo(root)
                target = root / '.codex/agents/rfc-worker.toml'
                if kind == 'parent':
                    outside = base / 'outside'; outside.mkdir()
                    (root / '.codex').symlink_to(outside, target_is_directory=True)
                else:
                    target.parent.mkdir(parents=True)
                    if kind == 'leaf':
                        target.symlink_to(SKILL_DIR / 'SKILL.md')
                    else:
                        target.write_text('mine' if kind == 'unknown' else '# Generated by implement-rfc/scripts/render_runtime_adapters.py (fake).')
                result = self.run_renderer(root)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse((root / '.claude').exists())
                self.assertFalse((root / '.mask/generated').exists())

    def test_legacy_copy_requires_external_context_without_touching_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'legacy'
            init_repo(root, token='legacy')
            context = root / '.mask/skill-config/implement-rfc'
            facts, rules = (context / 'project.json').read_bytes(), (context / 'project.md').read_bytes()
            shutil.rmtree(context)
            local = root / '.agents/skills/implement-rfc'
            shutil.copytree(SKILL_DIR, local)
            (local / 'config/project.json').write_bytes(facts)
            (local / 'references/project.md').write_bytes(rules)
            before = {str(p): p.read_bytes() for p in local.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, str(local / 'scripts/render_runtime_adapters.py'), '--repo-root', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('missing project configuration', result.stderr)
            self.assertEqual(before, {str(p): p.read_bytes() for p in local.rglob('*') if p.is_file()})

    def test_mask_locked_consumer_is_judged_by_lock_and_fresh_render(self):
        # The owner can move its lock without editing package input bytes.
        self.set_mask_paths('.mask/future/{skill}/roles.json', ['.mask/previous/{skill}/roles.json'])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(self.run_renderer(root).returncode, 0)
            # MASK publishes the same files under its own lock and never touches the
            # renderer's manifest; leave that manifest carrying digests from an older render.
            roles = []
            for path in sorted([*root.glob(".claude/agents/rfc-*.md"), *root.glob(".codex/agents/rfc-*.toml")]):
                roles.append({"agent": path.parts[-3].lstrip("."), "name": path.stem,
                              "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()})
            lock_path = root / ".mask/future/implement-rfc/roles.json"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(json.dumps({"schema": "mask.native-role-lock.v1", "schema_version": 1, "roles": roles}), encoding="utf-8")
            manifest_path = root / ".mask/generated/implement-rfc/runtime-adapters.json"
            manifest_path.write_text(manifest_path.read_text().replace("a", "b", 3), encoding="utf-8")
            check = self.run_renderer(root, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("ignored legacy adapter manifest", check.stderr)
            # Direct rendering would publish beside MASK's record; it is refused.
            direct = self.run_renderer(root)
            self.assertEqual(direct.returncode, 2)
            self.assertIn("run mask ensure", direct.stderr)
            # A file that no longer equals the fresh render is stale, and it no longer matches the lock either.
            drifted = root / ".codex/agents/rfc-worker.toml"
            original = drifted.read_text(encoding="utf-8")
            drifted.write_text(original + "# drift\n", encoding="utf-8")
            check = self.run_renderer(root, "--check")
            self.assertEqual(check.returncode, 1)
            self.assertIn("stale generated file", check.stderr)
            self.assertIn("lock drift", check.stderr)
            drifted.write_text(original, encoding="utf-8")
            # Files current but the lock disagreeing is drift for mask ensure, not staleness.
            lock = json.loads(lock_path.read_text())
            lock["roles"][0]["sha256"] = "0" * 64
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            check = self.run_renderer(root, "--check")
            self.assertEqual(check.returncode, 1)
            self.assertIn("lock drift", check.stderr)
            self.assertNotIn("stale generated file", check.stderr)

    def test_mask_path_discovery_refuses_unsupported_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.mask_stub.write_text('print("{}")\n')
            result = self.run_renderer(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn('does not advertise workflow paths', result.stderr)
            self.set_mask_paths('../outside/roles.json', [])
            result = self.run_renderer(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn('unsafe workflow paths', result.stderr)
            self.assertFalse((root / '.codex/agents').exists())

    def test_mask_retired_fallback_is_read_only_and_canonical_has_priority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.set_mask_paths('.mask/new/roles.json', ['.mask/old/roles.json'])
            self.assertEqual(self.run_renderer(root).returncode, 0)
            roles = [dict(agent=path.parts[-3].lstrip('.'), name=path.stem,
                          sha256=__import__('hashlib').sha256(path.read_bytes()).hexdigest())
                     for path in [*root.glob('.claude/agents/*'), *root.glob('.codex/agents/*')]]
            legacy = root / '.mask/old/roles.json'
            legacy.parent.mkdir(parents=True)
            legacy.write_text(json.dumps(dict(schema='mask.native-role-lock.v1', roles=roles)))
            self.assertEqual(self.run_renderer(root, '--check').returncode, 0)
            self.assertEqual(self.run_renderer(root).returncode, 2)
            canonical = root / '.mask/new/roles.json'
            canonical.parent.mkdir(parents=True)
            canonical.write_text('{}')
            self.assertEqual(self.run_renderer(root, '--check').returncode, 2)
            self.assertTrue(legacy.is_file())

    def test_noop_render_and_check_are_observational(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(self.run_renderer(root).returncode, 0)
            before = {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(self.run_renderer(root, '--check').returncode, 0)
            after = {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()

class ProfileTests(unittest.TestCase):
    def test_explicit_override_is_capability_checked(self):
        import render_runtime_adapters as renderer
        roles = renderer.load_json(SKILL_DIR / 'config/roles.json')['roles']
        profiles = renderer.load_json(SKILL_DIR / 'config/routing-profiles.json')
        baseline, _ = renderer.select_routes(ROUTING, roles, profiles)
        profiles['profiles']['test-candidate'] = {'overrides': {'codex': {'rfc-worker': {'model': 'gpt-6-astra', 'effort': 'low'}}}}
        with self.assertRaisesRegex(ValueError, 'unverified'):
            renderer.select_routes(ROUTING, roles, profiles, 'test-candidate')
        caps = {'codex': {'gpt-6-astra': ['low', 'high']}}
        candidate, receipt = renderer.select_routes(ROUTING, roles, profiles, 'test-candidate', caps)
        self.assertEqual(candidate['codex']['rfc-worker'], {'model':'gpt-6-astra','effort':'low'})
        for name in roles:
            if name != 'rfc-worker':
                self.assertEqual(candidate['codex'][name], baseline['codex'][name])
        self.assertEqual(candidate['claude'], baseline['claude'])
        self.assertIsNone(receipt['observed'])
        explicit = {'codex': {'rfc-worker': {'model':'gpt-6-astra','effort':'high'}}}
        resolved, receipt = renderer.select_routes(ROUTING, roles, profiles, 'test-candidate', caps,
                                                  explicit_routes=explicit)
        self.assertEqual(resolved['codex']['rfc-worker']['effort'], 'high')
        self.assertEqual(receipt['origins']['codex']['rfc-worker'], 'explicit_user')

    def test_public_profile_and_selection_preserve_native_settings(self):
        runner = RenderRuntimeAdaptersTests()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(runner.run_renderer(root).returncode, 0)
            config = root / '.codex/config.toml'
            config.write_text('model = "user-choice"\n')
            caps = root / 'caps.json'
            caps.write_text(json.dumps({'codex': {'gpt-6-astra':['low']}}))
            before = (root / '.codex/agents/rfc-reviewer.toml').read_text()
            refused = runner.run_renderer(root, '--profile', 'astra-low-first')
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual((root / '.codex/agents/rfc-reviewer.toml').read_text(), before)
            result = runner.run_renderer(root, '--profile', 'baseline')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(config.read_text(), 'model = "user-choice"\n')
            data = tomllib.loads((root / '.codex/agents/rfc-worker.toml').read_text())
            self.assertEqual(data['model'], 'gpt-6-astra')
            self.assertEqual(data['model_reasoning_effort'], 'low')
            profiles = json.loads((SKILL_DIR / 'config/routing-profiles.json').read_text())
            self.assertEqual(set(profiles['profiles']), {'baseline'})

    def test_fallback_never_assumes_capacity_or_effort(self):
        import render_runtime_adapters as renderer
        for reason in renderer.FALLBACK_REASONS:
            receipt = renderer.fallback_receipt({'model':'requested','effort':None}, reason)
            self.assertEqual(receipt['reason'], reason)
            self.assertIsNone(receipt['observed'])
        alt = {'provider':'codex','model':'explicit','effort':'none'}
        with self.assertRaises(ValueError):
            renderer.fallback_receipt({}, 'shared_quota', alternative=alt)
        approval = {'alternative':alt,'scope':'one-run','risk_floor':'review-high',
                    'permission_billing_boundary':'subscription/read-only','max_attempts':1}
        self.assertEqual(renderer.fallback_receipt({}, 'server_unavailability', alternative=alt,
                         approval=approval, attempt=1)['alternative'], alt)
        with self.assertRaises(ValueError):
            renderer.fallback_receipt({}, 'server_unavailability', alternative=alt,
                                      approval=approval, attempt=2)


class IntegratorRoutingTests(unittest.TestCase):
    def setUp(self):
        self.renderer = VALIDATOR_MODULE.renderer
        self.roles = self.renderer.validate_roles(self.renderer.load_json(SKILL_DIR / 'config/roles.json'))
        self.profiles = {'schema': 'implement-rfc.routing-profiles.v1', 'profiles': {'baseline': {}}}

    def test_independent_routes_and_explicit_precedence(self):
        import copy
        base, _ = self.renderer.select_routes(ROUTING, self.roles, self.profiles)
        changed = copy.deepcopy(ROUTING)
        for provider in ('codex', 'claude'):
            changed['providers'][provider]['classes']['balanced'] = {'model': 'scout', 'effort': 'low'}
            changed['providers'][provider]['classes']['standard'] = {'model': 'worker', 'effort': 'medium'}
            changed['session_routes']['rfc-coordinator'][provider] = {'model': 'coordinator', 'effort': 'low'}
        actual, receipt = self.renderer.select_routes(changed, self.roles, self.profiles)
        for provider in ('codex', 'claude'):
            self.assertEqual(actual[provider]['rfc-integrator'], base[provider]['rfc-integrator'])
            self.assertEqual(receipt['origins'][provider]['rfc-integrator'], 'integration_default')
            preserved = {provider: {'model': 'strong-prior', 'effort': 'high'}}
            caps = {provider: {'strong-prior': ['high'], 'explicit': ['xhigh']}}
            actual, receipt = self.renderer.select_routes(changed, self.roles, self.profiles,
                capabilities=caps, preserved_integrator_routes=preserved)
            self.assertEqual(actual[provider]['rfc-integrator'], preserved[provider])
            self.assertEqual(receipt['origins'][provider]['rfc-integrator'], 'preserved_owner')
            explicit = {provider: {'rfc-integrator': {'model': 'explicit', 'effort': 'xhigh'}}}
            actual, receipt = self.renderer.select_routes(changed, self.roles, self.profiles,
                capabilities=caps, preserved_integrator_routes=preserved, explicit_routes=explicit)
            self.assertEqual(actual[provider]['rfc-integrator'], explicit[provider]['rfc-integrator'])
            self.assertEqual(receipt['origins'][provider]['rfc-integrator'], 'explicit_user')
            self.assertIsNone(receipt['observed'])
            self.assertFalse(receipt['session_selection']['applied'])

    def test_unknown_authority_versions_and_missing_routes_refuse(self):
        import copy
        original = self.renderer.load_json(SKILL_DIR / 'config/roles.json')
        for change in ('unknown-version', 'unknown-role', 'leaf-delegation', 'recursive', 'old-field', 'entrypoint'):
            value = copy.deepcopy(original)
            if change == 'unknown-version': value['schema'] = 'implement-rfc.roles.v3'
            if change == 'unknown-role': value['roles']['rfc-surprise'] = value['roles']['rfc-worker']
            if change == 'leaf-delegation': value['roles']['rfc-worker']['delegation']['allowed_roles'] = ['rfc-utility']
            if change == 'recursive': value['roles']['rfc-integrator']['delegation']['allowed_roles'] = ['rfc-integrator']
            if change == 'old-field': value['roles']['rfc-worker']['may_spawn_utility'] = True
            if change == 'entrypoint': value['roles']['rfc-integrator']['entrypoint'] = '../escape.md'
            with self.subTest(change=change), self.assertRaises(ValueError): self.renderer.validate_roles(value)
        for change in ('missing-integration', 'missing-session', 'unknown-version', 'integrator-class', 'unknown-session'):
            value = copy.deepcopy(ROUTING)
            if change == 'missing-integration': del value['providers']['codex']['classes']['integration']
            if change == 'missing-session': del value['session_routes']
            if change == 'unknown-version': value['schema'] = 'implement-rfc.routing.v3'
            if change == 'integrator-class': value['assignments']['rfc-integrator'] = 'balanced'
            if change == 'unknown-session': value['session_routes']['rfc-extra'] = {}
            with self.subTest(change=change), self.assertRaises(ValueError): self.renderer.validate_routing(value, self.roles)
        for route in ({'model': 'prior'}, {'model': 'prior', 'effort': 'high'}):
            with self.assertRaises(ValueError):
                self.renderer.select_routes(ROUTING, self.roles, self.profiles,
                    preserved_integrator_routes={'codex': route})

    def test_public_override_binds_both_values_and_preserves_leaf_outputs(self):
        runner = RenderRuntimeAdaptersTests()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(runner.run_renderer(root).returncode, 0)
            leaves = {p: p.read_bytes() for family, suffix in (('codex', 'toml'), ('claude', 'md'))
                      for role in self.renderer.LEAF_ROLES
                      for p in [root / f'.{family}/agents/{role}.{suffix}']}
            prior = root / 'prior.json'; explicit = root / 'explicit.json'; caps = root / 'caps.json'
            prior.write_text(json.dumps({p: {'model': 'prior', 'effort': 'high'} for p in ('codex','claude')}))
            explicit.write_text(json.dumps({p: {'model': 'chosen', 'effort': 'xhigh'} for p in ('codex','claude')}))
            caps.write_text(json.dumps({p: {'prior': ['high'], 'chosen': ['xhigh']} for p in ('codex','claude')}))
            options = ('--preserved-integrator-route', str(prior), '--integrator-route', str(explicit))
            refused = runner.run_renderer(root, *options)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            args = (*options, '--capabilities', str(caps))
            result = runner.run_renderer(root, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
            codex = tomllib.loads((root / '.codex/agents/rfc-integrator.toml').read_text())
            self.assertEqual((codex['model'], codex['model_reasoning_effort']), ('chosen','xhigh'))
            self.assertTrue(codex['agents']['enabled'])
            self.assertNotIn('max_depth', codex['agents'])
            claude = (root / '.claude/agents/rfc-integrator.md').read_text()
            self.assertIn('model: "chosen"', claude); self.assertIn('effort: xhigh', claude)
            self.assertNotIn('permissionMode:', claude)
            for p, content in leaves.items(): self.assertEqual(p.read_bytes(), content)
            self.assertFalse((root / '.codex/agents/rfc-coordinator.toml').exists())
            self.assertFalse((root / '.claude/agents/rfc-coordinator.md').exists())
            self.assertEqual(runner.run_renderer(root, *args, '--check').returncode, 0)
            path = root / '.codex/agents/rfc-integrator.toml'; path.write_text(path.read_text() + '# owner edit\n')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(runner.run_renderer(root, *args).returncode, 2)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_public_session_selection_changes_no_native_agent_files(self):
        runner = RenderRuntimeAdaptersTests()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(runner.run_renderer(root).returncode, 0)
            agents = {p: p.read_bytes() for family in ('codex', 'claude')
                      for p in (root / f'.{family}/agents').iterdir()}
            settings = root / '.codex/config.toml'; settings.write_text('model = "owner-selected"\n')
            overlay = root / 'session.json'; caps = root / 'caps.json'
            overlay.write_text(json.dumps({'session_routes': {'rfc-coordinator': {
                'codex': {'model': 'session-choice', 'effort': 'medium'}}}}))
            caps.write_text(json.dumps({'codex': {'session-choice': ['medium']}}))
            result = runner.run_renderer(root, '--routing-override', str(overlay), '--capabilities', str(caps))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents, {p: p.read_bytes() for p in agents})
            self.assertEqual(settings.read_text(), 'model = "owner-selected"\n')
            manifest = json.loads((root / '.mask/generated/implement-rfc/runtime-adapters.json').read_text())
            session = manifest['routing_provenance']['session_selection']
            self.assertEqual(session['requested']['rfc-coordinator']['codex'], {'model':'session-choice','effort':'medium'})
            self.assertFalse(session['applied']); self.assertIsNone(session['observed'])


    def test_public_entrypoint_uses_each_providers_only_discovery_root(self):
        for provider, discovery, suffix in (('codex', '.agents', 'toml'), ('claude', '.claude', 'md')):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                init_repo(root)
                write_context(root, config=PROJECT)
                entry = root / discovery / 'skills/implement-rfc'
                entry.parent.mkdir(parents=True)
                entry.symlink_to(SKILL_DIR, target_is_directory=True)
                result = subprocess.run([sys.executable, '-B', str(entry / 'scripts/render_runtime_adapters.py'),
                                         '--repo-root', str(root)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                content = (root / f'.{provider}/agents/rfc-integrator.{suffix}').read_text()
                expected = f'{discovery}/skills/implement-rfc/references/milestone-integration.md'
                self.assertIn(expected, content)
                self.assertTrue((root / expected).is_file())
                other = '.agents' if discovery == '.claude' else '.claude'
                self.assertNotIn(f'{other}/skills/implement-rfc/references/milestone-integration.md', content)
                self.assertFalse((root / other / 'skills/implement-rfc').exists())
