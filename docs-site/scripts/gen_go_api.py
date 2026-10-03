#!/usr/bin/env python3
"""
Generate Go API reference using gomarkdoc.
Run from docs-site/ directory.
"""

import subprocess
import sys
from pathlib import Path

def main():
    docs_site = Path(__file__).parent.parent
    api_dir = docs_site / "docs" / "api" / "go"
    api_dir.mkdir(parents=True, exist_ok=True)

    go_src = Path(__file__).parent.parent.parent / "packages" / "rilavo-go"

    if not go_src.exists():
        print(f"⚠️  Go source not found at {go_src}")
        index_content = """---
title: Go API Reference
description: Complete API reference for the Rilavo Go SDK
---

# Go API Reference

> **Note**: Auto-generated API reference requires Go source to be available.
> Run `go install github.com/princjef/gomarkdoc/cmd/gomarkdoc@latest` then `gomarkdoc ./...` in `packages/rilavo-go/`.

## Quick Links

- [Installation](../sdks/go/index.md#installation)
- [Quick Start](../sdks/go/index.md#quick-start)
- [GitHub Source](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-go)
"""
        (api_dir / "index.md").write_text(index_content)
        return

    try:
        result = subprocess.run([
            "gomarkdoc", "./..."
        ], capture_output=True, text=True, cwd=go_src)

        if result.returncode == 0:
            (api_dir / "index.md").write_text(result.stdout)
            print("✅ Go API reference generated via gomarkdoc")
        else:
            print(f"⚠️  gomarkdoc failed: {result.stderr}")
            index_content = """---
title: Go API Reference
description: Complete API reference for the Rilavo Go SDK
---

# Go API Reference

Auto-generation failed. See source at [packages/rilavo-go](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-go).
"""
            (api_dir / "index.md").write_text(index_content)
    except FileNotFoundError:
        print("⚠️  gomarkdoc not available, creating placeholder")
        index_content = """---
title: Go API Reference
description: Complete API reference for the Rilavo Go SDK
---

# Go API Reference

> **Note**: Install gomarkdoc: `go install github.com/princjef/gomarkdoc/cmd/gomarkdoc@latest`

## Quick Links

- [Installation](../sdks/go/index.md#installation)
- [Quick Start](../sdks/go/index.md#quick-start)
- [GitHub Source](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-go)
"""
        (api_dir / "index.md").write_text(index_content)

if __name__ == "__main__":
    main()
