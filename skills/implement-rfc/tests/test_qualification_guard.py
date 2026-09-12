"""Public guard courses use only disposable temporary fixture state."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import write_context

SKILL = Path(__file__).resolve().parents[1]


class QualificationGuardTests(unittest.TestCase):
    def test_native_course_capture_api(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        from qualification_guard import capture_live, check_live
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            existing, missing = root / "roles.lock", root / "declaration.json"
            existing.write_bytes(b"original")
            before = capture_live([str(root)], [str(existing), str(missing)])
            self.assertEqual(check_live(before), [])
            existing.write_bytes(b"changed")
            missing.write_bytes(b"created")
            self.assertEqual(check_live(before), [str(existing), str(missing)])
            self.assertEqual(existing.read_bytes(), b"changed")

    def test_native_capture_detects_parent_escape_with_identical_bytes(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        from qualification_guard import capture_live, check_live
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            live, outside = root / "live", root / "outside"
            inside = live / "inside"
            inside.mkdir(parents=True)
            outside.mkdir()
            for directory in (inside, outside):
                (directory / "declaration.json").write_bytes(b"identical")
            selected = live / "selected"
            selected.symlink_to(inside, target_is_directory=True)
            declaration = selected / "declaration.json"
            missing = selected / "missing.json"
            before = capture_live([str(live)], [str(declaration), str(missing)])
            self.assertEqual(check_live(before), [])
            selected.unlink()
            selected.symlink_to(outside, target_is_directory=True)
            self.assertEqual(check_live(before), [str(declaration), str(missing)])

    def test_linked_consumers(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            for token in ("alpha", "beta"):
                with self.subTest(consumer=token):
                    consumer = base / token
                    facts = write_context(consumer, token=token)
                    self.assertEqual(facts["project"], token)
                    link = consumer / ".agents/skills/implement-rfc"
                    link.parent.mkdir(parents=True)
                    link.symlink_to(SKILL, target_is_directory=True)
                    live = base / (token + "-live")
                    live.mkdir()
                    declaration = live / ".mask.json"
                    declaration.write_bytes(b'{"skills":[]}\n')
                    missing = live / "missing.json"
                    helper = link / "scripts/qualification_guard.py"
                    prefix = [sys.executable, "-B", str(helper), "--allowed-root", str(consumer),
                              "--target-root", str(consumer), "--live-root", str(live),
                              "--live-file", str(declaration), "--live-file", str(missing)]

                    def run(code, options=None):
                        result = subprocess.run((options or prefix) + ["--", sys.executable, "-c", code],
                                                capture_output=True, text=True)
                        return result.returncode, json.loads(result.stdout)

                    code, receipt = run("import os,pathlib; pathlib.Path('result').write_text(os.environ['QUALIFICATION_TARGET_ROOT'])")
                    self.assertEqual(code, 0)
                    self.assertEqual((consumer / "result").read_text(), str(consumer))
                    self.assertTrue(all(row["unchanged"] for row in receipt["live_files"]))
                    self.assertFalse(receipt["live_files"][1]["before"]["exists"])
                    code, receipt = run("raise SystemExit(7)")
                    self.assertEqual((code, receipt["status"], receipt["command_returncode"]), (4, "command-failed", 7))

                    escape = consumer / "escape"
                    escape.symlink_to(live, target_is_directory=True)
                    for target in (live, escape):
                        options = prefix.copy()
                        options[options.index("--target-root") + 1] = str(target)
                        code, receipt = run("raise RuntimeError('must never execute')", options)
                        self.assertEqual((code, receipt["status"], receipt["command_returncode"]), (2, "refused", None))
                    options = prefix.copy()
                    options[options.index("--allowed-root") + 1] = str(base)
                    self.assertEqual(run("pass", options)[0], 2)
                    options = prefix.copy()
                    options[options.index("--live-file") + 1] = str(consumer / "result")
                    self.assertEqual(run("pass", options)[0], 2)

                    # The simulated live files also belong to this temporary fixture.
                    for path, operation in ((declaration, "write_bytes(b'changed')"),
                                            (declaration, "unlink()"),
                                            (missing, "write_bytes(b'created')")):
                        code, receipt = run(f"from pathlib import Path; Path({str(path)!r}).{operation}; raise SystemExit(9)")
                        self.assertEqual((code, receipt["status"], receipt["command_returncode"]), (3, "drift", 9))
                    code, receipt = run(f"from pathlib import Path; Path({str(missing)!r}).unlink(); Path({str(missing)!r}).symlink_to({str(consumer / 'result')!r})")
                    self.assertEqual((code, receipt["status"]), (3, "drift"))


if __name__ == "__main__":
    unittest.main()
