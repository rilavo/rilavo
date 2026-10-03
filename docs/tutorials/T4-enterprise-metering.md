# T4 — Enterprise metering walkthrough (E-14 + E-07 tier boundary)

**What you'll do:** watch usage become billable exactly per E-14/E-07 rules,
and see the soft tier boundary behave. Runs against the real enterprise
modules in `rilavo-enterprise/`.

```bash
cd /home/admin/rilavo/rilavo-enterprise
uv sync
```

## Walkthrough

```python
from rilavo_enterprise.metering import MeteringLedger, month_key
from rilavo_enterprise.tiers import TierManager

ledger = MeteringLedger(free_allowance_per_month=10_000)  # E-07 starting default
tiers = TierManager(ledger)
NOW = 1_760_000_000                                       # our simulated "now"

# A month of traffic: 500 calls beyond the free allowance:
for i in range(10_500):
    ledger.record("acme", "verify", ts=NOW + i)

# Check the tier boundary AS OF a moment inside that month (always pass the
# time you mean -- wall-clock defaults are for live services):
state = tiers.check("acme", now=NOW + 11_000)
print(state.value)                        # -> warning  (soft boundary, grace running)

print(ledger.billable("acme", month_key(NOW)))            # -> 500
print("%.2f" % ledger.invoice("acme", month_key(NOW)))    # -> 0.50  ($0.001 x 500)

# Crossing the allowance is remembered for E-07's conversion metric:
print("acme" in tiers.crossings)          # -> True
```

## What the numbers are — and are not

- **10,000 allowance / $0.001 rate**: illustrative starting values (E-07/E-14).
  Both are constructor parameters; the docs mark them Open until real cost
  data exists (E-16). Change them freely; nothing here hardcodes them.
- **Soft warning, not cutoff**: crossing the allowance yields `warning`, then
  `grace_ended` after the grace period — never an immediate stop (E-7 edge case).
- **Burst traffic bills identically** to steady state — no burst pricing at v0.

**Back to:** [Tutorials index](index.md)
