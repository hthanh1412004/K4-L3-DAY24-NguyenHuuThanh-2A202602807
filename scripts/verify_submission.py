"""Run final checks, then capture the post-test dpo replay on localhost."""
import hashlib
import json
import os
import subprocess
import sys
import threading
import socket
from pathlib import Path

from agent import ledger
from sink.sink import create_server, reset_log

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
QUERY = "Tổng hợp các ticket còn mở tuần này"


def main():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PRE_COMMIT_HOME"] = str(ROOT / ".cache/pre-commit")
    env["PATH"] = str(ROOT / ".tools/gitleaks-v8.30.1") + os.pathsep + env["PATH"]
    before = REPORTS / "attack-before.log"
    before_hash = hashlib.sha256(before.read_bytes()).hexdigest()

    def run(name, command, expected=0):
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
        (REPORTS / f"cp5-{name}.log").write_bytes(result.stdout + result.stderr)
        if result.returncode != expected:
            raise RuntimeError(f"{name}: exit {result.returncode}, see reports/cp5-{name}.log")
        print(f"{name}: exit {result.returncode}")
        return result

    run("tests", [sys.executable, "-X", "utf8", "-m", "pytest", "tests/", "-q", "-s"])
    run("lures", [sys.executable, "-X", "utf8", "-m", "agent.check_lure", "corpus/ticket-90*.md"])
    ledger_path = REPORTS / "ledger.jsonl"
    first_line = len(ledger_path.read_text(encoding="utf-8").splitlines()) + 1
    with socket.socket() as probe:
        running = probe.connect_ex(("127.0.0.1", 10024)) == 0
    server = None if running else create_server()
    if server is not None:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        reset_log()
        run("replay", [sys.executable, "-X", "utf8", "-m", "agent.loop", "--mock", "--as", "dpo", QUERY])
        after = REPORTS / "attack-after.log"
        after.write_bytes((REPORTS / "sink.log").read_bytes())
        assert after.read_bytes() == b"", "Post-containment sink must be empty"
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
    assert hashlib.sha256(before.read_bytes()).hexdigest() == before_hash
    assert ledger.verify(ledger_path)
    entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    assert all(all(e.get(k) for k in ("reason", "agent_id", "run_id", "on_behalf_of", "expires_at")) for e in entries)
    last_run = entries[first_line - 1:]
    assert all(e["on_behalf_of"] == "dpo" for e in last_run)
    assert any(e["tool"] == "read_customer" and e["decision"] == "allow" for e in last_run)
    assert any(e["tool"] == "http_post" and e["decision"] == "deny" for e in last_run)
    run("ledger", [sys.executable, "-c", "from agent.ledger import verify; from pathlib import Path; assert verify(Path('reports/ledger.jsonl')); print(True)"])
    scanner = str(ROOT / ".tools/gitleaks-v8.30.1/gitleaks.exe")
    run("scanner-version", [scanner, "version"])
    run("history", [scanner, "git", "--config", ".gitleaks.toml", "--redact", "--no-color", "--report-format", "json", "--report-path", "reports/cp5-history.json", "."], 1)
    run("current", [scanner, "dir", "--config", ".gitleaks.toml", "--redact", "--no-color", "--report-format", "json", "--report-path", "reports/cp5-current.json", "."])
    assert len(json.loads((REPORTS / "cp5-history.json").read_text(encoding="utf-8"))) == 1
    assert json.loads((REPORTS / "cp5-current.json").read_text(encoding="utf-8")) == []
    run("pre-commit", [sys.executable, "-m", "pre_commit", "run", "--all-files"])
    summary = {
        "query": QUERY, "principal": "dpo", "mock": True,
        "ledger_first_line": first_line, "ledger_last_line": len(entries),
        "ledger_verify": True, "attack_after_bytes": 0, "attack_before_sha256": before_hash,
        "read_customer_allow_count": sum(e["tool"] == "read_customer" and e["decision"] == "allow" for e in last_run),
        "http_post_deny_lines": [i for i,e in enumerate(entries,1) if i >= first_line and e["tool"] == "http_post" and e["decision"] == "deny"],
        "history_findings": 1, "current_findings": 0, "pre_commit_exit": 0,
    }
    (REPORTS / "cp5-evidence.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Final ledger lines {first_line}-{len(entries)}; after log=0 bytes; verify=True")


if __name__ == "__main__":
    main()
