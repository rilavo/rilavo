# SDK Parity Audit Manifest

Status: OPEN (#34) — structural audit only; full byte-for-byte harness deferred.

Authoritative SDK: Python (`rilavo-protocol`).
Golden fixtures: `golden/golden.json`, `golden/rejects.json`.

Per-language state:
- Python: 196 pass / 1 skip; uses `tests/test_golden_corpus.py`
- Go (`packages/rilavo-go`): 10/10 PASS; `testdata/golden.json` (copy)
- TS (`packages/rilavo-ts`): 18/18 PASS; inline vectors (not reading golden/)
- Next (`packages/rilavo-next`): 3/3 PASS; middleware only
- WP (`packages/rilavo-wp`): 14/14 (`check.php`)

Open gaps:
- TS uses inline golden vectors (not shared `golden/` file) — future work.
- No middleware-specific test file in `rilavo-next`.
- Smoke/doctor real env checks deferred from C32/C33.
- No `benchmark_all_sdks.py` byte-for-byte comparison (this manifest only).

Wire/protocol: untouched. Registry: human-gated.
