"""Public trail-digest courses over two differently configured linked fixture consumers."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import CONFIG, git, init_repo, write_context

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import progress_trail  # noqa: E402

ALT = copy.deepcopy(CONFIG)
ALT.update(project="beta", display_name="Beta", session_prefix="beta", origin_repo_name="beta", issue_root="work/board",
           lanes={"inbox": "in", "backlog": "later", "ready": "ready", "in_progress": "doing",
                  "parked": "parked", "blocked": "blocked", "done": "shipped"},
           lane_statuses={"in": "Inbox", "later": "Backlog", "ready": "Ready", "doing": "In Progress",
                          "parked": "Parked", "blocked": "Blocked", "shipped": "Done"})


def tree_digest(root: Path) -> str:
    """Every byte under the consumer, Git internals included; the helper must change none."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() or p.is_symlink()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes() if path.is_file() else str(path.readlink()).encode())
    return digest.hexdigest()


class ProgressTrailTests(unittest.TestCase):
    def consumer(self, base: Path, token: str, config: dict | None):
        root = base / token
        # Detached maintenance can remove its lock after a fixture commit returns.
        # Keep fixture writers quiescent across the whole-tree preservation checks.
        facts = init_repo(root, token=token, auto_maintenance=False)
        if config is not None:
            facts = write_context(root, config=config)
            git(root, "add", ".mask")
            git(root, "commit", "-m", "alternate context")
        lanes, issue_root = facts["lanes"], facts["issue_root"]
        for lane in lanes.values():
            (root / issue_root / lane).mkdir(parents=True, exist_ok=True)
            (root / issue_root / lane / ".gitkeep").write_text("")
        card = root / issue_root / lanes["ready"] / "FX-0007-first-card.md"
        card.write_text("---\nid: FX-0007\n---\n# FX-0007\n")
        (root / ".gitignore").write_text(".agents/\n")
        git(root, "add", ".")
        git(root, "commit", "-m", "board")
        link = root / ".agents/skills/implement-rfc"
        link.parent.mkdir(parents=True)
        link.symlink_to(SKILL, target_is_directory=True)
        return root, facts, card

    def run_helper(self, link: Path, *options: str):
        result = subprocess.run([sys.executable, "-B", str(link / "scripts/progress_trail.py"), *options],
                                capture_output=True, text=True)
        return result.returncode, result.stdout.splitlines(), result.stderr

    def test_one_shot_digest_over_linked_consumers(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            for token, config in (("alpha", None), ("beta", ALT)):
                with self.subTest(consumer=token):
                    root, facts, card = self.consumer(base, token, config)
                    lanes, issue_root = facts["lanes"], facts["issue_root"]
                    link = root / ".agents/skills/implement-rfc"
                    baseline = git(root, "rev-parse", "HEAD")
                    before = tree_digest(root)

                    code, lines, _ = self.run_helper(link, "--repo-root", str(root), "--since", baseline, "--json")
                    self.assertEqual(code, 0)
                    kinds = [json.loads(line)["kind"] for line in lines]
                    self.assertEqual(kinds, ["in-flight", "cursor"])
                    self.assertEqual(json.loads(lines[-1])["commit"], baseline)
                    self.assertEqual(tree_digest(root), before)

                    # Claim: the card moves lanes in one commit (rename-shaped).
                    claimed = root / issue_root / lanes["in_progress"] / card.name
                    git(root, "mv", str(card), str(claimed))
                    git(root, "commit", "-m", "Claim FX-0007")
                    # Scoped source commit.
                    (root / "src.txt").write_text("work\n")
                    git(root, "add", "src.txt")
                    git(root, "commit", "-m", "FX-0007: add the source")
                    # Finish: a rewritten card lands in done (delete-plus-add shaped).
                    done = root / issue_root / lanes["done"] / card.name
                    claimed.unlink()
                    done.write_text("---\nid: FX-0007\nstatus: Done\n---\n# FX-0007\n\nAccepted with a long record.\n" * 5)
                    git(root, "add", "-A", issue_root)
                    git(root, "commit", "-m", "Finish FX-0007")
                    # Pending park of a second card plus in-flight source edits.
                    second = root / issue_root / lanes["ready"] / "FX-0008-second.md"
                    second.write_text("---\nid: FX-0008\n---\n")
                    git(root, "add", str(second))
                    git(root, "commit", "-m", "Add FX-0008")
                    second.rename(root / issue_root / lanes["parked"] / second.name)
                    (root / "src.txt").write_text("more work\n")
                    (root / "new.txt").write_text("new\n")

                    before = tree_digest(root)
                    code, lines, _ = self.run_helper(link, "--repo-root", str(root), "--since", baseline)
                    self.assertEqual(code, 0)
                    self.assertEqual(tree_digest(root), before)
                    texts = [line[6:] for line in lines[:-1]]  # strip HH:MM
                    self.assertTrue(texts[0].startswith(f"claim FX-0007 ({lanes['ready']} > {lanes['in_progress']})"), texts)
                    self.assertTrue(texts[1].startswith("commit ") and texts[1].endswith("FX-0007: add the source"), texts)
                    self.assertTrue(texts[2].startswith(f"finish FX-0007 ({lanes['in_progress']} > {lanes['done']})"), texts)
                    self.assertTrue(texts[3].startswith("commit ") and texts[3].endswith("Add FX-0008"), texts)
                    self.assertEqual(texts[4], f"pending park FX-0008 ({lanes['ready']} > {lanes['parked']})")
                    self.assertEqual(texts[5], "in-flight 2 paths (+2 -0)")
                    self.assertEqual(lines[-1], "cursor " + git(root, "rev-parse", "HEAD"))
                    self.assertEqual(len(lines), 7)

                    # A commit that is only a board move emits one transition, not a commit line too.
                    self.assertFalse(any(t.startswith("commit ") and "Claim" in t for t in texts))

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, _, _ = self.consumer(base, "alpha", None)
            link = root / ".agents/skills/implement-rfc"
            unmanaged = base / "unmanaged"
            unmanaged.mkdir()
            git(unmanaged, "init", "-b", "main")
            for options in ((["--repo-root", str(base / "missing")]),
                            (["--repo-root", str(unmanaged)]),
                            (["--repo-root", str(root / ".mask")]),
                            (["--repo-root", str(root), "--since", "not-a-commit"]),
                            (["--repo-root", str(root), "--since", "0" * 40])):
                with self.subTest(options=options):
                    code, lines, err = self.run_helper(link, *options)
                    self.assertEqual((code, lines), (2, []))
                    self.assertIn("refused", err)
            code, _, err = self.run_helper(link)
            self.assertEqual(code, 2)
            code, _, err = self.run_helper(link, "--repo-root", str(root), "--follow", "--since", "HEAD")
            self.assertEqual(code, 2)

    def test_follow_coalesces_and_rate_limits(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, facts, card = self.consumer(base, "beta", ALT)
            lanes, issue_root = facts["lanes"], facts["issue_root"]
            trail = progress_trail.Trail(str(root))
            follower = progress_trail.Follower(trail, min_gap=600, quiet_after=1800, as_json=True, start=1000.0)
            self.assertEqual(follower.poll(1030.0), [])

            claimed = root / issue_root / lanes["in_progress"] / card.name
            git(root, "mv", str(card), str(claimed))
            git(root, "commit", "-m", "Claim FX-0007")
            (root / "a.txt").write_text("a\n")
            # Inside the gap: observed and held, nothing emitted.
            self.assertEqual(follower.poll(1060.0), [])
            (root / "a.txt").write_text("aa\n")
            git(root, "add", "a.txt")
            git(root, "commit", "-m", "FX-0007: a")
            (root / "b.txt").write_text("b\n")
            self.assertEqual(follower.poll(1090.0), [])
            # Gap elapsed: one burst carrying every held event and the in-flight delta.
            burst = [json.loads(line) for line in follower.poll(1600.0)]
            self.assertEqual([e["kind"] for e in burst], ["transition", "commit", "in-flight"])
            self.assertEqual(burst[0]["action"], "claim")
            self.assertEqual(burst[1]["subject"], "FX-0007: a")
            self.assertEqual((burst[2]["count"], burst[2]["added"], burst[2]["removed"]), (1, 1, 0))
            # Quiet: an unchanged in-flight set emits nothing, even past the heartbeat.
            self.assertEqual(follower.poll(2200.0), [])
            self.assertEqual(follower.poll(3500.0), [])
            # Heartbeat reports only a changed in-flight set.
            (root / "c.txt").write_text("c\n")
            self.assertEqual(follower.poll(3600.0), [])  # last flush 3500, quiet_after not elapsed
            beat = [json.loads(line) for line in follower.poll(5400.0)]
            self.assertEqual([(e["kind"], e["count"], e["added"]) for e in beat], [("in-flight", 2, 1)])
            # A pending move is reported once, then again only if it changes.
            second = root / issue_root / lanes["ready"] / "FX-0008-second.md"
            second.write_text("x")
            git(root, "add", str(second))
            git(root, "commit", "-m", "Add FX-0008")
            moved = root / issue_root / lanes["blocked"] / second.name
            second.rename(moved)
            first = [json.loads(line) for line in follower.poll(7000.0)]
            self.assertEqual([e["kind"] for e in first], ["commit", "pending"])
            self.assertEqual((first[1]["action"], first[1]["to"]), ("block", lanes["blocked"]))
            self.assertEqual(follower.poll(8000.0), [])
            moved.rename(root / issue_root / lanes["parked"] / second.name)
            again = [json.loads(line) for line in follower.poll(9000.0)]
            self.assertEqual([(e["kind"], e["action"]) for e in again], [("pending", "park")])


if __name__ == "__main__":
    unittest.main()
