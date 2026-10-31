"""RFC-ASK-0018 AC01: a never-enabled session behaves identically before and after publication.

Runs one command sequence (init, prepare, loopback serve, import, observe, pause,
start, hand-back, a failing ready, status, conflicts, resume-development, stop)
through the RFC_BASE_SHA helper and the working-tree helper in disposable roots,
then compares exit codes, stdout, stderr, hosting keys, files and session bytes after
normalizing only random/time fields (session/preparation IDs, tokens, ports, PIDs,
times, temporary paths). Usage: python ac01_differential.py [BASE_REVISION]
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BASE = sys.argv[1] if len(sys.argv) > 1 else "ff6b40727e673cf4defd9a6cbaca7816558eb1de"
SOURCE = "skills/attended-review"


def run(script, tmp):
    root = tmp / "checkout"; root.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("ATTENDED_REVIEW_")}
    def command(*args):
        return [sys.executable, "-B", str(script), "--repo-root", str(root), "--registry", str(tmp / "registry"), *args]
    def cli(*args):
        p = subprocess.run(command(*args), capture_output=True, text=True, env=env, timeout=30)
        return p.returncode, p.stdout, p.stderr
    (tmp / "manifest.json").write_text(json.dumps({"schema_version": 1, "candidates": [
        {"id": c, "title": c, "revision": "1", "criteria": ["x"]} for c in "AB"]}))
    out = [cli("init", "--manifest", str(tmp / "manifest.json")), cli("prepare")]
    state = json.loads(out[-1][1])
    fingerprint = {c["id"]: c["fingerprint"] for c in state["candidates"]}
    (tmp / "decision.json").write_text(json.dumps({"schema_version": 1, "session": state["session"], "decisions": [
        {"candidate": "A", "fingerprint": fingerprint["A"], "decision_id": "d", "outcome": "accept"}]}))
    host = subprocess.Popen(command("serve"), stdout=subprocess.PIPE, text=True, env=env)
    hosting = json.loads(host.stdout.readline())
    for args in (("import", "--file", str(tmp / "decision.json")), ("observe", "B", "--evidence", "e"), ("pause",),
                 ("start",), ("hand-back",), ("ready", "Z", "--evidence", "x"), ("status",), ("conflicts",),
                 ("resume-development", "--candidate", "B"), ("status", "--after", "0")):
        out.append(cli(*args))
    out.append(cli("stop")); host.wait(timeout=10); host.stdout.close()
    out.append(cli("status", "--full"))
    files = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
    return out, sorted(hosting), files, json.loads((root / ".mask/attended-review/session.json").read_text())


def normal(value, tmp):
    text = json.dumps(value, sort_keys=True).replace(json.dumps(str(tmp))[1:-1], "TMP")
    for pattern, replacement in ((r'\d{4}-\d\d-\d\dT[\d:.+]+', 'TIME'), (r'[0-9a-f]{32}', 'SID'),
                                 (r'(preparation_id\\?"?: ?\\?")[0-9a-f]{16}', r'\1PREP'),
                                 (r'(port\\?"?: ?)\d+', r'\1PORT'), (r'127\.0\.0\.1:\d+', '127.0.0.1:PORT'),
                                 (r'(pid\\?"?: ?)\d+', r'\1PID'), (r'token=[A-Za-z0-9_-]{40,}', 'token=TOKEN'),
                                 (r'(token[^:=]*[:=] ?\\?"?)[A-Za-z0-9_-]{40,}', r'\1TOKEN')):
        text = re.sub(pattern, replacement, text)
    return text


def main():
    work = Path(tempfile.mkdtemp(prefix="ac01-"))
    try:
        baseline = work / "baseline"
        (baseline / "scripts").mkdir(parents=True)
        (baseline / "scripts" / "attended_review.py").write_bytes(subprocess.run(
            ["git", "-C", str(REPO), "show", f"{BASE}:{SOURCE}/scripts/attended_review.py"], capture_output=True, check=True).stdout)
        shutil.copytree(REPO / SOURCE / "assets", baseline / "assets")
        results = []
        for name, script in (("baseline", baseline / "scripts" / "attended_review.py"),
                             ("candidate", REPO / SOURCE / "scripts" / "attended_review.py")):
            tmp = (work / f"run-{name}").resolve()
            tmp.mkdir()
            results.append(normal(run(script, tmp), tmp))
        if results[0] != results[1]:
            print("DIFFERENT"); return 1
        print(f"identical: {len(results[0])} normalized bytes; baseline {BASE}")
        return 0
    finally:
        shutil.rmtree(work)


if __name__ == "__main__":
    sys.exit(main())
