"""C2 rot-guards: execute the tutorial code paths so docs cannot silently rot.

T1/T3 python blocks are extracted verbatim from docs/tutorials/*.md and run
in order in one namespace. T2's command sequence is exercised against an
ephemeral port with temp paths.
"""

from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TUT = REPO / "docs" / "tutorials"
PY = sys.executable


def _blocks(md_path: Path) -> list[str]:
    text = md_path.read_text()
    return re.findall(r"```python\n(.*?)```", text, flags=re.S)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str, timeout: float = 15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("server not healthy")


def test_tutorials_exist():
    for name in ("index.md", "T1-verify-your-first-credential.md",
                 "T2-self-host-an-issuer.md", "T3-mock-checkout.md",
                 "T4-production-deployment.md"):
        assert (TUT / name).exists(), f"missing tutorial {name}"


def test_T1_blocks_run_in_sequence():
    ns: dict = {}
    blocks = _blocks(TUT / "T1-verify-your-first-credential.md")
    assert len(blocks) >= 4
    for i, block in enumerate(blocks):
        exec(compile(block, f"<T1 block {i}>", "exec"), ns)


def test_T3_blocks_run_and_line_count_claim_holds():
    ns: dict = {}
    blocks = _blocks(TUT / "T3-mock-checkout.md")
    assert len(blocks) >= 2
    for block in blocks:
        exec(compile(block, "<T3>", "exec"), ns)

    # Honest line-count check, counted from the tutorial's own code block:
    middleware_block = next(b for b in blocks if "def authorize_checkout" in b)
    body_lines = []
    in_body = False
    for line in middleware_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("def authorize_checkout"):
            in_body = True
            continue
        if in_body:
            if line.startswith((" ", "\t")) and stripped and not stripped.startswith("#"):
                body_lines.append(stripped)
            elif stripped:
                break
    assert 1 < len(body_lines) <= 9      # single-digit, per P-20 claim


def test_T2_command_sequence_works(tmp_path):
    key = tmp_path / "my_issuer.pem"
    entry = tmp_path / "my_directory_entry.json"

    step1 = subprocess.run([PY, "-m", "rilavo.cli", "keygen",
                            "--out", str(key)],
                           stdout=open(entry, "w"), stderr=subprocess.PIPE,
                           text=True, cwd=str(REPO), timeout=60)
    assert step1.returncode == 0
    doc = json.loads(entry.read_text())
    assert doc["issuer_id"].startswith("rilavo:iss:")

    port = _free_port()
    server = subprocess.Popen(
        [PY, str(REPO / "deploy" / "selfhosted" / "server.py"),
         "--key", str(key), "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(REPO))
    try:
        _wait(f"http://127.0.0.1:{port}/health")
        drill = subprocess.run(
            [PY, str(REPO / "deploy" / "selfhosted" / "client_drill.py"),
             "--server", f"http://127.0.0.1:{port}"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO))
        assert drill.returncode == 0, drill.stderr
        assert '"accepted": true' in drill.stdout
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def test_tutorial_index_links_resolve():
    index = (TUT / "index.md").read_text()
    for link in re.findall(r"\]\(([^)]+\.md)\)", index):
        assert (TUT / link).exists(), f"broken tutorial link: {link}"
