"""P-22 threat-model traceability validators (C5).

Locks `docs/threat_model_summary.md` and the security docs to reality:

- every STRIDE threat row from `docs/wave_2/22_SECURITY_THREAT_MODEL.md`
  must appear in the summary matrix (no dropped rows);
- every test named in either security document must exist in an actual
  suite by def name (a renamed/deleted test fails CI until the doc is
  updated in the same change);
- coverage claims must be honest: a row may claim COVERED only when it
  names at least one existing test; the known correlation gap stays
  marked as instrumentation-only / OPEN, never "covered";
- the responsible-disclosure contact stays a PLACEHOLDER and the
  disclosure window stays OPEN (no number invented) per P-23/E-13;
- the P-22 re-audit trigger is preserved.

Nothing here validates security behavior itself -- the conformance,
correlation, and boundary suites do that. These tests only guarantee the
traceability documents cannot silently drift from the code they cite.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = REPO_ROOT / "rilavo-protocol"
SUMMARY = REPO_ROOT / "docs" / "threat_model_summary.md"
THREAT_DOC = REPO_ROOT / "docs" / "wave_2" / "22_SECURITY_THREAT_MODEL.md"
PROTO_SECURITY = PROTOCOL_ROOT / "SECURITY.md"
TOP_SECURITY = REPO_ROOT / "SECURITY.md"
TEST_DIRS = [REPO_ROOT / "tests", PROTOCOL_ROOT / "tests", REPO_ROOT / "rilavo-enterprise" / "tests"]


def _all_test_defs():
    defs = set()
    for d in TEST_DIRS:
        for p in sorted(d.glob("test_*.py")):
            defs |= set(re.findall(r"^def (test_\w+)", p.read_text(), re.MULTILINE))
    return defs


def _matrix_rows():
    """Rows of the summary table after the header, as tuples of cells."""
    rows = []
    for line in SUMMARY.read_text().splitlines():
        if line.startswith("|") and not set(line) <= {"|", "-", " ", ":"}:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "Category":
                continue
            rows.append(cells)
    return rows


def _p22_threat_lines():
    """The *Threat:* bullet lines of the P-22 source doc, verbatim text."""
    text = THREAT_DOC.read_text()
    out = []
    for m in re.finditer(r"\*(Threat(?:\s*\([^)]*\))?):\*\s*(.+)", text):
        out.append(m.group(2).strip())
    return out


def _test_refs(text):
    return sorted(set(re.findall(r"`(test_\w+?)((?:\[\*\])?)`", text)))


STOPWORDS = {
    "a", "an", "the", "of", "to", "for", "and", "or", "via", "any",
    "without", "than", "that", "this", "not", "be", "is", "it", "its",
}


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).split()


def test_every_p22_threat_row_present_in_summary():
    """Each *Threat:* bullet of the P-22 doc must map to a matrix row.

    Matching is by significant-word coverage of the row's Category+Threat
    cells -- robust to minor wording differences, strict enough that a
    silently dropped or replaced row fails.
    """
    threats = _p22_threat_lines()
    assert len(threats) == 11, f"P-22 defines 11 threat rows, found {len(threats)}"
    rows = [" ".join(r[:2]) for r in _matrix_rows()]

    for t in threats:
        sig = [w for w in _norm(t) if w not in STOPWORDS]
        matched = [row for row in rows if all(w in _norm(row) for w in sig)]
        assert matched, f"P-22 row missing from summary matrix: {t!r}"


def test_summary_has_one_row_per_p22_threat_no_extras():
    rows = _matrix_rows()
    assert len(rows) == 11
    categories = [r[0] for r in rows]
    assert categories.count("Spoofing") == 2
    assert categories.count("Tampering") == 2
    assert categories.count("Repudiation") == 1
    assert categories.count("Information Disclosure") == 2
    assert categories.count("Denial of Service") == 2
    assert categories.count("Elevation of Privilege") == 2


def test_every_test_referenced_by_summary_exists():
    defs = _all_test_defs()
    refs = [n for n, suffix in _test_refs(SUMMARY.read_text())]
    missing = [n for n in refs if n not in defs]
    assert not missing, f"summary cites tests that do not exist: {missing}"


def test_every_test_referenced_by_security_docs_exists():
    defs = _all_test_defs()
    refs = []
    for doc in (PROTO_SECURITY, TOP_SECURITY):
        refs += [n for n, suffix in _test_refs(doc.read_text())]
    missing = [n for n in sorted(set(refs)) if n not in defs]
    assert not missing, f"security docs cite nonexistent tests: {missing}"


def test_covered_rows_name_existing_tests():
    for row in _matrix_rows():
        status = row[-1]
        cited = [n for n, _ in _test_refs(row[3])]
        existing = [n for n in cited if n in _all_test_defs()]
        if status.startswith("COVERED"):
            assert existing, f"COVERED claimed with no valid test: {row[1]!r}"
        else:
            assert "OPEN" in status or "instrumentation" in status.lower(), (
                f"row neither COVERED nor honestly open: {status!r}"
            )


def test_residual_correlation_gap_stays_honestly_open():
    text = SUMMARY.read_text().lower()
    assert "residual gap" in text or "residual" in text
    assert "open per p-13" in text or ("open" in text and "p-13" in text)
    # the instrumentation module must not be described as enforcement
    assert "enforcement-only" not in text


def test_disclosure_contact_is_placeholder_and_window_open():
    for doc in (TOP_SECURITY, PROTO_SECURITY):
        text = doc.read_text()
        assert re.search("placeholder", text, re.IGNORECASE), f"{doc.name}: contact must stay a placeholder"
        assert re.search(r"disclosure window.{0,80}OPEN", text, re.DOTALL | re.IGNORECASE), (
            f"{doc.name}: disclosure window must stay OPEN"
        )
        # no committed number of days/months anywhere near 'window'
        assert not re.search(r"window[^.]*\b\d+\s*(day|month|year)", text, re.IGNORECASE), (
            f"{doc.name}: a disclosure window length was hardcoded"
        )


def test_reaudit_trigger_preserved():
    trigger = re.compile(
        r"P-0?6.{0,40}P-0?7.{0,40}P-0?9", re.DOTALL
    )
    assert trigger.search(PROTO_SECURITY.read_text()), (
        "protocol SECURITY.md lost the P-06/P-07/P-09 re-audit trigger"
    )


def test_summary_points_back_at_p22_source_and_scope_boundary():
    text = SUMMARY.read_text()
    assert "22_SECURITY_THREAT_MODEL.md" in text
    top = TOP_SECURITY.read_text()
    assert "threat_model_summary.md" in top
    assert "out of scope" in top.lower() or "scope boundary" in top
