"""Rilavo doctor: end-to-end install health check."""
from __future__ import annotations

from . import __version__ as rilavo_version


def check_on_path(cmd: str) -> tuple[bool, str]:
    import shutil
    path = shutil.which(cmd)
    return (path is not None, f"{cmd} on PATH" if path else f"{cmd} NOT on PATH")


def check_import(module: str) -> tuple[bool, str]:
    try:
        __import__(module)
        return True, f"import {module}: OK"
    except Exception as e:
        return False, f"import {module}: FAILED ({e})"


def check_smoke() -> tuple[bool, str]:
    try:
        from .smoke import run_smoke
        ok, _ = run_smoke(verbose=False)
        return (ok, "rilavo smoke: PASS") if ok else (False, "rilavo smoke: FAIL")
    except Exception as e:
        return False, f"rilavo smoke: ERROR ({e})"


def check_online_verifier() -> tuple[bool, str]:
    # Optional: try to reach a public verifier endpoint if configured
    # For now, this is a placeholder — real implementation would hit a known verifier
    return True, "online check: SKIPPED (no endpoint configured)"


def check_redis_nonce_cache() -> tuple[bool, str]:
    """Check Redis nonce cache connectivity if configured.
    Returns (True, "SKIPPED") if not configured, otherwise checks connectivity."""
    import os
    redis_url = os.environ.get("RILAVO_REDIS_URL")
    if not redis_url:
        return True, "Redis nonce cache: SKIPPED (RILAVO_REDIS_URL not set)"

    try:
        import redis
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=3, socket_timeout=3)
        client.ping()
        return True, f"Redis nonce cache: CONNECTED ({redis_url})"
    except Exception as e:
        return False, f"Redis nonce cache: FAILED ({e})"


def check_issuer_directory() -> tuple[bool, str]:
    """Check issuer directory connectivity if configured.
    Returns (True, "SKIPPED") if not configured, otherwise checks connectivity."""
    import os
    dir_url = os.environ.get("RILAVO_ISSUER_DIR_URL")
    if not dir_url:
        return True, "Issuer directory: SKIPPED (RILAVO_ISSUER_DIR_URL not set)"

    try:
        import requests
        response = requests.get(f"{dir_url.rstrip('/')}/health", timeout=3)
        if response.status_code == 200:
            return True, f"Issuer directory: CONNECTED ({dir_url})"
        return False, f"Issuer directory: HTTP {response.status_code} ({dir_url})"
    except Exception as e:
        return False, f"Issuer directory: FAILED ({e})"


def check_revocation_log() -> tuple[bool, str]:
    """Check revocation log connectivity if configured.
    Returns (True, "SKIPPED") if not configured, otherwise checks connectivity."""
    import os
    rev_url = os.environ.get("RILAVO_REVOCATION_LOG_URL")
    if not rev_url:
        return True, "Revocation log: SKIPPED (RILAVO_REVOCATION_LOG_URL not set)"

    try:
        import requests
        response = requests.get(f"{rev_url.rstrip('/')}/health", timeout=3)
        if response.status_code == 200:
            return True, f"Revocation log: CONNECTED ({rev_url})"
        return False, f"Revocation log: HTTP {response.status_code} ({rev_url})"
    except Exception as e:
        return False, f"Revocation log: FAILED ({e})"



def run_doctor(online: bool = False) -> tuple[bool, list[str]]:
    results: list[tuple[bool, str]] = []
    results.append(check_on_path("rilavo"))
    results.append(check_import("rilavo"))
    results.append(check_import("rilavo.smoke"))
    results.append(check_smoke())
    if online:
        results.append(check_online_verifier())
        results.append(check_redis_nonce_cache())
        results.append(check_issuer_directory())
        results.append(check_revocation_log())

    all_ok = all(r[0] for r in results)
    lines = ["Rilavo Doctor — Install Health Check", f"rilavo version: {rilavo_version}", ""]
    for ok, msg in results:
        prefix = "✅" if ok else "❌"
        lines.append(f"{prefix}  {msg}")
    lines.append("")
    lines.append("✅ ALL CHECKS PASSED" if all_ok else "❌ SOME CHECKS FAILED")
    if not all_ok:
        lines.append("Run 'rilavo explain <code>' for any failure reason codes.")
    return all_ok, lines


def cmd_doctor(online: bool = False) -> int:
    """CLI entry point. Returns exit code (0=pass, 1=fail)."""
    ok, lines = run_doctor(online)
    for line in lines:
        print(line)
    return 0 if ok else 1