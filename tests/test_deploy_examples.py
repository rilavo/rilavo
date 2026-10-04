"""P-31 deployment-path regression tests.

Guarantees the README walkthroughs keep working: every command documented in
deploy/*/README.md is exercised here on an ephemeral port. If one of these
fails, a README has rotted.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str, timeout: float = 15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(0.05)
    raise RuntimeError(f"server never became healthy: {url}")


def test_embedded_verify_app_runs_green():
    proc = subprocess.run(
        [PY, str(REPO / "deploy" / "embedded" / "verify_app.py")],
        capture_output=True, text=True, timeout=60, cwd=str(REPO))
    assert proc.returncode == 0, proc.stderr
    assert '"accepted": true' in proc.stdout
    assert "verifier ready:" in proc.stdout


def test_selfhosted_keygen_server_client_drill(tmp_path):
    key = tmp_path / "issuer.pem"
    entry = tmp_path / "directory_entry.json"

    # Step 1: rilavo keygen
    with open(entry, "w") as out:
        proc = subprocess.run([PY, "-m", "rilavo.cli", "keygen", "--out", str(key)],
                              stdout=out, stderr=subprocess.PIPE,
                              text=True, timeout=60, cwd=str(REPO))
    assert proc.returncode == 0 and key.exists()
    doc = json.loads(entry.read_text())
    assert doc["issuer_id"].startswith("rilavo:iss:")

    # Steps 2+3: server under that key, then the client drill
    port = _free_port()
    server = subprocess.Popen(
        [PY, str(REPO / "deploy" / "selfhosted" / "server.py"),
         "--key", str(key), "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=str(REPO))
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


def test_hosted_no_docker_fallback_service_healthy():
    port = _free_port()
    cmd = ("from rilavo.service import RilavoService; import threading; "
           "s = RilavoService(port=%d).start(); "
           "print('hosted issuer live on', s.url, flush=True); "
           "threading.Event().wait()" % port)
    server = subprocess.Popen([PY, "-c", cmd], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, cwd=str(REPO))
    try:
        _wait(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/directory",
                                    timeout=5) as r:
            entry = r.status, r.read()
        assert b'"issuer_id": "rilavo:iss:' in entry[1]
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def test_hosted_compose_file_is_valid_yaml_and_well_formed():
    yaml = pytest.importorskip("yaml")   # compose runtime validation needs a
                                         # docker host; YAML parse needs PyYAML
    path = REPO / "deploy" / "hosted" / "docker-compose.yml"
    doc = yaml.safe_load(path.read_text())
    svc = doc["services"]["rilavo-hosted"]
    assert svc["build"]["dockerfile"] == "deploy/hosted/Dockerfile"
    assert "8090:8090" in svc["ports"]
    assert svc["healthcheck"]["retries"] >= 1
