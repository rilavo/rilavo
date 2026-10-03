# Golden-vector cross-language test corpus (P5-B)

Single source of truth for wire-compatibility fixtures, generated from the
Python reference implementation by `rilavo-protocol/scripts/generate_golden_vectors.py`.

## Files
- `golden.json` — JCS canonicalization cases, PoP payload (hex), issuer/agent
  public keys, a fully issued credential (fields + `sig`), and its PoP signature.
  The embedded request shape is `GET /data/1` with action class `data.read`
  (the shape the language suites rehearse).
- `rejects.json` — deterministic reject cases (`unknown_version`,
  `wrong_audience`, `expired`) with the exact reason code each implementation
  must produce.

## Consumers
| Suite | How it consumes this corpus |
|---|---|
| Python (`rilavo-protocol/tests/test_golden_corpus.py`) | reads these files directly |
| Go (`packages/rilavo-go/testdata/golden.json`) | byte-identical copy; drift-guarded by the Python test |
| TypeScript (`packages/rilavo-ts/tests/index.test.ts`) | currently carries the same vectors inline (P1-A2/A3); migration to read this corpus is future work |

## Regeneration
```
cd rilavo-protocol && uv run python scripts/generate_golden_vectors.py
cp ../golden/golden.json ../packages/rilavo-go/testdata/golden.json
```
Vectors are regenerated with fresh keys each run; consumers only rely on
internal consistency, never hardcoded key material.
