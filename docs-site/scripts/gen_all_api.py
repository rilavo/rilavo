#!/usr/bin/env python3
"""
Generate all API references.
Run from docs-site/ directory.
"""

import subprocess
import sys
from pathlib import Path

def run_script(name, script_path):
    print(f"
{'='*60}")
    print(f"Generating {name} API reference...")
    print(f"{'='*60}")
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {name}: {e}")
        return False

def main():
    scripts_dir = Path(__file__).parent
    results = {}

    results["Python"] = run_script("Python", scripts_dir / "gen_python_api.py")
    results["TypeScript"] = run_script("TypeScript", scripts_dir / "gen_ts_api.py")
    results["Go"] = run_script("Go", scripts_dir / "gen_go_api.py")

    print(f"
{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    if all(results.values()):
        print("
✅ All API references generated successfully")
        return 0
    else:
        print("
⚠️  Some generations failed (check output above)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
