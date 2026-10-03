"""Console entry point: run the hosted protocol service.

Environment:
    PORT         listen port (default 8090)
"""

from __future__ import annotations

import os
import threading


def main() -> int:
    port = int(os.environ.get("PORT", "8090"))
    from .service import RilavoService
    svc = RilavoService(port=port).start()
    print(f"rilavo hosted service live on {svc.url}", flush=True)
    threading.Event().wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
