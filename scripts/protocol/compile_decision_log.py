#!/usr/bin/env python3
"""C3/P-44: compile both repositories' DECISION_LOG.md files plus the Master
Dependency Register statuses into one regenerable DECISION_LOG_COMPILED.md.

REGENERABLE BY DESIGN (P-44): the output is always produced by this script
and never hand-edited. Re-run after any log change; idempotent for identical
inputs.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
REGISTER = ROOT / "docs" / "Rilavo_Master_Dependency_Register.md"


def parse_register_statuses() -> dict[str, str]:
    """Extract ID -> Status for every P-XX / E-XX row of the register."""
    if not REGISTER.exists():
        return {}
    text = REGISTER.read_text()
    statuses: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"\| ([PE]-\d{2}) \|", line)
        if not m:
            continue
        parts = [p.strip() for p in line.split("|")]
        # columns: '', ID, Document, Priority, Depends-on, Status, Closes-when
        if len(parts) >= 7:
            statuses[m.group(1)] = parts[6] or parts[5]
    return statuses


def status_for(traces: str, item_id: str,
               register: dict[str, str]) -> str:
    """Status column value. Register items take their register status
    verbatim; infra/log entries are 'Decided' by construction."""
    ids = re.findall(r"[PE]-\d{2}", traces + " " + item_id)
    known = [register[i] for i in dict.fromkeys(ids) if i in register]
    if known:
        return "; ".join(dict.fromkeys(known))
    return "Decided"


def parse_log(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        m = re.match(r"^\| (\S+) \| 2026-08 \| (.*?) \| (.*?) \|$", line)
        if m:
            rows.append({"id": m.group(1), "decision": m.group(2),
                         "traces": m.group(3)})
    return rows


def compile_all() -> dict:
    register = parse_register_statuses()
    sections = []
    n = 0
    for label, log_path in (
            ("rilavo-protocol (protocol decisions)",
             REPO / "DECISION_LOG.md"),
            ("rilavo-commercial (commercial-layer decisions)",
             ROOT / "rilavo-commercial" / "DECISION_LOG.md")):
        rows = parse_log(log_path)
        section_rows = []
        for row in rows:
            n += 1
            status = status_for(row["traces"], "", register)
            section_rows.append(
                f"| {n} | {row['id']} | {row['decision']} | "
                f"{row['traces']} | {status} |")
        sections.append((label, log_path.name, len(rows), section_rows))

    header_lines = [
        "# Rilavo — Compiled Decision Log",
        "",
        "**Regenerable artifact** — produced by "
        "`scripts/compile_decision_log.py`; NEVER hand-edit. Re-run after any "
        "change to either repository's DECISION_LOG.md (P-44 practice: one "
        "current source of truth per decision).",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Status values are pulled from `Rilavo_Master_Dependency_Register.md` "
        "where the traced item has a register row; entries whose trace targets "
        "are process/infrastructure rather than register items read 'Decided'.",
        "",
    ]
    for label, fname, count, rows in sections:
        header_lines += [f"## {label} — `{fname}` ({count} entries)", "",
                         "| # | Log ref | Decision | Traces to | Status |",
                         "|---|---|---|---|---|"]
        header_lines += [r + "" for r in rows]
        header_lines.append("")
    return "\n".join(header_lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(REPO / "DECISION_LOG_COMPILED.md"))
    args = ap.parse_args(argv)
    compiled = compile_all()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    previous = out.read_text() if out.exists() else None
    body = compiled.split("\n", 3)[3] if "\n" in compiled else ""
    # Idempotency: regenerate everything EXCEPT the generation timestamp when
    # content is unchanged -- compare body sans timestamp line.
    if previous:
        prev_body = "\n".join(previous.splitlines()[5:])
        new_body = "\n".join(compiled.splitlines()[5:])
        if prev_body == new_body:
            print(f"idempotent: {out} unchanged (timestamp refreshed only)")
    out.write_text(compiled)
    print(f"compiled decision log written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
