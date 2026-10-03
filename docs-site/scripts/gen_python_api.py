#!/usr/bin/env python3
"""
Generate Python API reference documentation using mkdocstrings.
Run from docs-site/ directory.
"""

import subprocess
import sys
from pathlib import Path

def main():
    docs_site = Path(__file__).parent.parent
    api_dir = docs_site / "docs" / "api" / "python"
    api_dir.mkdir(parents=True, exist_ok=True)

    # Generate index.md for Python API
    index_content = """---
title: Python API Reference
description: Complete API reference for the Rilavo Python SDK
---

# Python API Reference

::: rilavo
    options:
      show_source: true
      show_root_heading: true
      show_root_toc_entry: false
      docstring_style: google
      docstring_section_style: table
      merge_init_into_class: true
      separate_signature: true
"""
    (api_dir / "index.md").write_text(index_content)
    print(f"✅ Generated {api_dir / 'index.md'}")

    # Generate module-specific pages
    modules = [
        "api", "canonical", "cli", "compact", "compat", "credential",
        "diagnostics", "directory_signing", "discovery", "discovery_client",
        "doctor", "enrollment", "errors", "fastapi", "init_scaffold",
        "keys", "middleware", "nonce_backends", "observability", "pop",
        "receipts", "revocation", "runbook", "service", "verifier", "testing"
    ]

    for mod in modules:
        mod_content = f"""---
title: rilavo.{mod}
description: API reference for rilavo.{mod}
---

# rilavo.{mod}

::: rilavo.{mod}
    options:
      show_source: true
      show_root_heading: true
      show_root_toc_entry: false
      docstring_style: google
      docstring_section_style: table
      merge_init_into_class: true
      separate_signature: true
"""
        (api_dir / f"{mod}.md").write_text(mod_content)

    print(f"✅ Generated {len(modules)} module pages")

if __name__ == "__main__":
    main()
