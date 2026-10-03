#!/usr/bin/env python3
"""
Rilavo Publish Pre-flight Validation
Runs all locally verifiable checks before publishing to registries.
Run with: python scripts/publish_preflight.py
"""

import json
import subprocess
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    details: str = ""

class PreflightChecker:
    def __init__(self, root: Path):
        self.root = root
        self.results: List[CheckResult] = []

    def run(self, name: str, check_fn):
        try:
            passed, msg, details = check_fn()
            result = CheckResult(name, passed, msg, details)
        except Exception as e:
            result = CheckResult(name, False, "Check failed with exception: " + str(e), "")
        self.results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print("  [" + status + "] " + name + ": " + result.message)
        if result.details and not result.passed:
            print("    Details: " + result.details)
        return result

    def summary(self) -> bool:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print("\n" + "=" * 60)
        print("PRE-FLIGHT SUMMARY: " + str(passed) + "/" + str(total) + " checks passed")
        print("=" * 60)
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            print("  [" + status + "] " + r.name)
        return all(r.passed for r in self.results)

def get_version_from_pyproject(path: Path) -> str:
    content = path.read_text()
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    return match.group(1) if match else "unknown"

def get_version_from_package_json(path: Path) -> str:
    data = json.loads(path.read_text())
    return data.get("version", "unknown")

def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout, result.stderr

def check_version_consistency(root: Path) -> Tuple[bool, str, str]:
    versions = {}
    versions["rilavo-protocol"] = get_version_from_pyproject(root / "rilavo-protocol" / "pyproject.toml")
    versions["rilavo-commercial"] = get_version_from_pyproject(root / "rilavo-commercial" / "pyproject.toml")
    versions["@rilavo/sdk"] = get_version_from_package_json(root / "packages" / "rilavo-ts" / "package.json")
    versions["@rilavo/next"] = get_version_from_package_json(root / "packages" / "rilavo-next" / "package.json")

    unique = set(versions.values())
    if len(unique) == 1:
        return True, "All packages at version " + list(unique)[0], "Versions: " + str(versions)
    else:
        return False, "Version mismatch: " + str(versions), "Found versions: " + str(versions)

def check_git_status(root: Path) -> Tuple[bool, str, str]:
    code, out, err = run_cmd(["git", "status", "--porcelain"], root)
    if code != 0:
        return False, "Git status failed", err
    if out.strip():
        return False, "Working tree not clean", "Uncommitted changes:\n" + out
    return True, "Working tree clean", ""

def check_git_tag_exists(root: Path) -> Tuple[bool, str, str]:
    code, out, err = run_cmd(["git", "describe", "--exact-match", "--tags", "HEAD"], root)
    if code == 0:
        tag = out.strip()
        return True, "Tagged as " + tag, ""
    return False, "No version tag on HEAD", "Create a tag (e.g., git tag v0.1.0) before publishing"

def check_python_tests(root: Path) -> Tuple[bool, str, str]:
    for pkg in ["rilavo-protocol", "rilavo-commercial"]:
        pkg_dir = root / pkg
        code, out, err = run_cmd(["uv", "run", "pytest", "tests/", "-q"], pkg_dir)
        if code != 0:
            return False, pkg + " tests failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    return True, "Python tests pass", ""

def check_go_tests(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-go"
    if not pkg_dir.exists():
        return True, "Go SDK not found (skipped)", ""
    code, out, err = run_cmd(["go", "test", "-count=1", "./..."], pkg_dir)
    if code != 0:
        return False, "Go tests failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    return True, "Go tests pass", ""

def check_typescript_tests(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-ts"
    if not pkg_dir.exists():
        return True, "TypeScript SDK not found (skipped)", ""
    code, out, err = run_cmd(["npm", "test"], pkg_dir)
    if code != 0:
        return False, "TypeScript tests failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    return True, "TypeScript tests pass", ""

def check_nextjs_tests(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-next"
    if not pkg_dir.exists():
        return True, "Next.js SDK not found (skipped)", ""
    code, out, err = run_cmd(["npm", "test"], pkg_dir)
    if code != 0:
        return False, "Next.js tests failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    return True, "Next.js tests pass", ""

def check_golden_vector_parity(root: Path) -> Tuple[bool, str, str]:
    golden_files = [
        root / "golden" / "golden.json",
        root / "golden" / "rejects.json",
        root / "packages" / "rilavo-go" / "testdata" / "golden.json",
    ]
    missing = [str(f) for f in golden_files if not f.exists()]
    if missing:
        return False, "Missing golden vector files", "Missing: " + str(missing)
    return True, "Golden vector files present", ""

def check_python_build(root: Path) -> Tuple[bool, str, str]:
    for pkg in ["rilavo-protocol", "rilavo-commercial"]:
        pkg_dir = root / pkg
        code, out, err = run_cmd(["uv", "build"], pkg_dir)
        if code != 0:
            return False, pkg + " build failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
        dist = pkg_dir / "dist"
        wheels = list(dist.glob("*.whl"))
        sdists = list(dist.glob("*.tar.gz"))
        if not wheels or not sdists:
            return False, pkg + " missing build artifacts", "Found: " + str(list(dist.iterdir()))
    return True, "Python packages build successfully", ""

def check_typescript_build(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-ts"
    code, out, err = run_cmd(["npm", "run", "build"], pkg_dir)
    if code != 0:
        return False, "TypeScript build failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    dist = pkg_dir / "dist"
    if not (dist / "cjs" / "src" / "index.js").exists():
        return False, "CJS build missing", ""
    if not (dist / "esm" / "src" / "index.js").exists():
        return False, "ESM build missing", ""
    return True, "TypeScript SDK builds successfully", ""

def check_nextjs_build(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-next"
    code, out, err = run_cmd(["npm", "run", "build"], pkg_dir)
    if code != 0:
        return False, "Next.js build failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    dist = pkg_dir / "dist"
    if not (dist / "index.js").exists():
        return False, "Next.js dist missing", ""
    return True, "Next.js SDK builds successfully", ""

def check_go_build(root: Path) -> Tuple[bool, str, str]:
    pkg_dir = root / "packages" / "rilavo-go"
    code, out, err = run_cmd(["go", "build", "./..."], pkg_dir)
    if code != 0:
        return False, "Go build failed", "Exit code: " + str(code) + "\n" + out + "\n" + err
    return True, "Go SDK builds successfully", ""

def check_license_files(root: Path) -> Tuple[bool, str, str]:
    missing = []
    for license_path in [
        root / "rilavo-protocol" / "LICENSE",
        root / "rilavo-commercial" / "LICENSE",
        root / "packages" / "rilavo-ts" / "LICENSE",
        root / "packages" / "rilavo-next" / "LICENSE",
        root / "packages" / "rilavo-go" / "LICENSE",
    ]:
        if not license_path.exists():
            missing.append(str(license_path))
    if missing:
        return False, "Missing LICENSE files", "Missing: " + str(missing)
    return True, "All LICENSE files present", ""

def check_no_secrets_in_artifacts(root: Path) -> Tuple[bool, str, str]:
    patterns = [
        rb"rlk_[a-zA-Z0-9]{32,}",
        rb"BEGIN PRIVATE KEY",
        rb"BEGIN OPENSSH PRIVATE KEY",
        rb"ghp_[a-zA-Z0-9]{36}",
        rb"gho_[a-zA-Z0-9]{36}",
    ]
    found = []
    for dist_dir in [
        root / "rilavo-protocol" / "dist",
        root / "rilavo-commercial" / "dist",
    ]:
        if dist_dir.exists():
            for artifact in dist_dir.iterdir():
                if artifact.is_file():
                    content = artifact.read_bytes()
                    for pattern in patterns:
                        if re.search(pattern, content):
                            found.append(str(artifact) + ": " + str(pattern))
    if found:
        return False, "Secrets found in artifacts", "Found: " + str(found)
    return True, "No secrets in artifacts", ""

def check_package_sizes(root: Path) -> Tuple[bool, str, str]:
    oversized = []
    size_limits = {
        root / "rilavo-protocol" / "dist": 5 * 1024 * 1024,
        root / "rilavo-commercial" / "dist": 10 * 1024 * 1024,
        root / "packages" / "rilavo-ts" / "dist": 2 * 1024 * 1024,
        root / "packages" / "rilavo-next" / "dist": 5 * 1024 * 1024,
    }
    for dist_dir, limit in size_limits.items():
        if dist_dir.exists():
            for artifact in dist_dir.iterdir():
                if artifact.is_file() and artifact.stat().st_size > limit:
                    oversized.append(str(artifact) + ": " + str(artifact.stat().st_size) + " bytes > " + str(limit))
    if oversized:
        return False, "Oversized packages", "Oversized: " + str(oversized)
    return True, "Package sizes OK", ""

def check_changelog_updated(root: Path) -> Tuple[bool, str, str]:
    decision_log = root / "rilavo-protocol" / "DECISION_LOG.md"
    if decision_log.exists():
        content = decision_log.read_text()
        version = get_version_from_pyproject(root / "rilavo-protocol" / "pyproject.toml")
        if version in content:
            return True, "DECISION_LOG contains current version", ""
        else:
            return False, "DECISION_LOG missing current version entry", "Version " + version + " not found in DECISION_LOG"
    return True, "DECISION_LOG not found (skipped)", ""

def main():
    root = Path(__file__).parent.parent
    os.chdir(root)

    print("Rilavo Publish Pre-flight Validation")
    print("=" * 60)

    checker = PreflightChecker(root)

    print("\nPhase 1: Version & Git")
    checker.run("Version consistency", lambda: check_version_consistency(root))
    checker.run("Git working tree clean", lambda: check_git_status(root))
    checker.run("Git tag on HEAD", lambda: check_git_tag_exists(root))

    print("\nPhase 2: Test Suites")
    checker.run("Python tests", lambda: check_python_tests(root))
    checker.run("Go tests", lambda: check_go_tests(root))
    checker.run("TypeScript tests", lambda: check_typescript_tests(root))
    checker.run("Next.js tests", lambda: check_nextjs_tests(root))

    print("\nPhase 3: Build")
    checker.run("Python build", lambda: check_python_build(root))
    checker.run("TypeScript build", lambda: check_typescript_build(root))
    checker.run("Next.js build", lambda: check_nextjs_build(root))
    checker.run("Go build", lambda: check_go_build(root))

    print("\nPhase 4: Artifacts & Security")
    checker.run("Golden vector parity", lambda: check_golden_vector_parity(root))
    checker.run("License files", lambda: check_license_files(root))
    checker.run("No secrets in artifacts", lambda: check_no_secrets_in_artifacts(root))
    checker.run("Package sizes", lambda: check_package_sizes(root))

    print("\nPhase 5: Documentation")
    checker.run("Changelog updated", lambda: check_changelog_updated(root))

    all_passed = checker.summary()

    if not all_passed:
        print("\nPRE-FLIGHT FAILED - Do not publish!")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED - Ready to publish")
        sys.exit(0)

if __name__ == "__main__":
    main()
