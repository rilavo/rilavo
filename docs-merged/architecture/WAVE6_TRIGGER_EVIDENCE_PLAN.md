# Wave-6 Trigger Evidence Plan

## Purpose

Defines exactly what pilot evidence would satisfy P-34's trigger: "v0 proves
single-hop authorization is constraining real integrations." All indicators are
measurable from pilot_metrics.py output or platform service logs.

## Measurable Indicators

| Indicator | Collection Method | Threshold (parameterized) |
|---|---|---|
| Batch-issue uptake rate | Count POST /batch-issue vs POST /issue per customer per week | >20% of active customers using batch |
| Multi-audience session length | Count distinct `aud` values per agent per session window | Median session touches >=5 audiences |
| Re-issuance frequency | Distribution of time between successive do_issue calls for same agent+audience pair | Median re-issuance interval < credential TTL/2 |
| Cross-verifier sub reuse | correlation.py monitor output from production traffic | Detected reuse rate >0% confirms the gap is real |

## Decision Thresholds (PROPOSED -- not decided)

These are parameterized proposals, not committed values:
- Trigger fires if >=3 of 4 indicators exceed their thresholds simultaneously
  across two consecutive weekly measurement windows.
- A single indicator exceeding threshold is insufficient (could be noise).
- The decision to proceed past the trigger requires human review of the
  evidence, not automatic activation.

## Design-Review Checklist (gates any future delegation work)

1. Confirm trigger evidence is from a real integration, not synthetic.
2. Verify no Wave-6 code was written before this review.
3. Confirm P-06 freeze status has not been declared prematurely.
4. Review delegation credential fields for scope-narrowing compliance.
5. Confirm revocation cascade design covers delegated credentials.
6. Obtain legal sign-off on data-handling implications of delegation.
