#!/usr/bin/env python3
"""
Generate TypeScript API reference using typedoc.
Run from docs-site/ directory.
"""

import subprocess
import sys
from pathlib import Path

def main():
    docs_site = Path(__file__).parent.parent
    api_dir = docs_site / "docs" / "api" / "typescript"
    api_dir.mkdir(parents=True, exist_ok=True)

    ts_src = Path(__file__).parent.parent.parent / "packages" / "rilavo-ts" / "src"

    if not ts_src.exists():
        print(f"⚠️  TypeScript source not found at {ts_src}")
        # Create placeholder
        index_content = """---
title: TypeScript API Reference
description: Complete API reference for the Rilavo TypeScript SDK
---

# TypeScript API Reference

> **Note**: Auto-generated API reference requires TypeScript source to be available.
> Run `npm run docs:api` in `packages/rilavo-ts/` to generate.

## Quick Links

- [Installation](../sdks/typescript/index.md#installation)
- [Quick Start](../sdks/typescript/index.md#quick-start)
- [GitHub Source](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-ts/src)
"""
        (api_dir / "index.md").write_text(index_content)
        return

    # Run typedoc to generate markdown
    try:
        result = subprocess.run([
            "npx", "typedoc",
            "--plugin", "typedoc-plugin-markdown",
            "--out", str(api_dir),
            "--entryPointStrategy", "expand",
            "--entryPoints", str(ts_src),
            "--name", "Rilavo TypeScript SDK",
            "--readme", "none",
            "--excludeInternal",
            "--excludePrivate",
            "--excludeProtected",
        ], capture_output=True, text=True, cwd=ts_src.parent)

        if result.returncode == 0:
            print("✅ TypeScript API reference generated via typedoc")
        else:
            print(f"⚠️  typedoc failed: {result.stderr}")
            # Create fallback
            index_content = """---
title: TypeScript API Reference
description: Complete API reference for the Rilavo TypeScript SDK
---

# TypeScript API Reference

Auto-generation failed. See source at [packages/rilavo-ts/src](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-ts/src).
"""
            (api_dir / "index.md").write_text(index_content)
    except FileNotFoundError:
        print("⚠️  npx/typedoc not available, creating placeholder")
        index_content = """---
title: TypeScript API Reference
description: Complete API reference for the Rilavo TypeScript SDK
---

# TypeScript API Reference

> **Note**: Install dependencies and run `npm run docs:api` in `packages/rilavo-ts/` to generate.

## Quick Links

- [Installation](../sdks/typescript/index.md#installation)
- [Quick Start](../sdks/typescript/index.md#quick-start)
- [GitHub Source](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-ts/src)
"""
        (api_dir / "index.md").write_text(index_content)

if __name__ == "__main__":
    main()
