# T4 — Product Metering Walkthrough (10 minutes)

> **Want to see how usage tracking and tier limits work?** This tutorial demonstrates the commercial product's metering and tier system using the real `rilavo-commercial` modules.

---

## What You'll Do

Watch usage become billable exactly per the metering rules, and see the soft tier boundary behave. Runs against the real product modules in `rilavo-commercial/`.

---

## Prerequisites
- **Python 3.11+**
- **uv** for package management
- Access to `rilavo-commercial/` (the commercial product modules)

---

## Walkthrough

```bash
cd /home/admin/rilavo/rilavo-commercial
uv sync
```

```python
from rilavo.metering import MeteringLedger, month_key
from rilavo.tiers import TierManager

ledger = MeteringLedger(free_allowance_per_month=10_000)  # E-07 starting default
tiers = TierManager(ledger)
NOW = 1_760_000_000                                       # our simulated "now"

# A month of traffic: 500 calls beyond the free allowance:
for i in range(10_500):
    ledger.record(month_key(NOW), 1)

# Check the bill
usage = ledger.usage(month_key(NOW))
print(f"Total usage: {usage}")  # 10,500
print(f"Billable: {tiers.billable(month_key(NOW))}")  # 500

# Now cross the tier boundary
for i in range(90_000):
    ledger.record(month_key(NOW), 1)

usage = ledger.usage(month_key(NOW))  # 100,500
tier = tiers.tier_for(usage)
print(f"Tier: {tier.name}, limit: {tier.limit}")
print(f"Overage: {max(0, usage - tier.limit)}")
```

---

## What Just Happened

| Step | What Happened | Why It Matters |
|------|---------------|----------------|
| 1 | Created ledger with 10,000 free/month | E-07: configurable free allowance |
| 2 | Recorded 10,500 calls | 500 billable (first 10k free) |
| 3 | Added 90,000 more calls | Crossed into next tier |
| 4 | Tier upgraded automatically | Soft boundary — no hard cutoff |
| 5 | Overage calculated correctly | Transparent, auditable billing |

---

## Key Concepts

### MeteringLedger (E-14)
Immutable append-only log of usage events. Each record: `(month_key, count, timestamp)`. Immutable — you can't delete or modify history.

### TierManager (E-07)
Defines tier boundaries and pricing. Default tiers:

| Tier | Monthly Limit | Per-Call Cost | Notes |
|------|---------------|---------------|-------|
| Free | 10,000 | $0.00 | Default allowance |
| Pro | 100,000 | $0.001/call | Soft boundary |
| Unlimited | Unlimited | Custom | Contract pricing |

### Soft Boundary (The Key Feature)
When usage exceeds a tier's limit, the system **does not hard-block**. Instead:
1. Overage is tracked separately
2. Tier upgrades are **soft** — service continues uninterrupted
3. Overage is billed at the next tier's rate
4. Customer can upgrade proactively or accept overage charges

This is a **business decision**, not a technical limitation. Hard blocking would break legitimate traffic during traffic spikes.

---

## The Metering Pipeline

```
Agent Request
    ↓
Verifier (fail-closed)
    ↓
MeteringLedger.record()  →  Immutable append
    ↓
TierManager.tier_for()  →  Current tier
    ↓
Billing (async)  →  Monthly invoice
```

---

## Key Concepts Explained

### Why Immutable Ledger?
Once a usage event is recorded, it **cannot be deleted or modified**. This provides:
- **Audit trail**: Full history for audits
- **Dispute resolution**: Undisputable evidence
- **Regulatory compliance**: Meets financial record requirements

### Why Soft Boundaries?
Hard blocking at tier boundaries would break legitimate traffic during traffic spikes. The soft boundary approach:
- **Service continuity**: No dropped requests at tier boundaries
- **Predictable costs**: Overage billed at known next-tier rate
- **Customer control**: Upgrade proactively or accept overage

### Tier Configuration
All tier parameters are **injectable configuration**, not hardcoded:
```python
tiers = TierManager(
    ledger,
    tiers={
        "free": Tier(limit=10_000, cost_per_call=0.0),
        "pro": Tier(limit=100_000, cost_per_call=0.001),
        "unlimited": Tier(limit=None, cost_per_call=0.0),  # unlimited
    }
)
```

---

## Running the Walkthrough

```bash
cd /home/admin/rilavo/rilavo-commercial
uv sync
python -c "
from rilavo.metering import MeteringLedger, month_key
from rilavo.tiers import TierManager

ledger = MeteringLedger(free_allowance_per_month=10_000)
tiers = TierManager(ledger)
NOW = 1_760_000_000

for i in range(10_500):
    ledger.record(month_key(NOW), 1)

print(f'Usage: {ledger.usage(month_key(NOW))}')
print(f'Billable: {tiers.billable(month_key(NOW))}')

for i in range(90_000):
    ledger.record(month_key(NOW), 1)

usage = ledger.usage(month_key(NOW))
tier = tiers.tier_for(usage)
print(f'Tier: {tier.name}, Overage: {max(0, usage - tier.limit)}')
"
```

---

## Expected Output
```
Usage: 10500
Billable: 500
Tier: pro, Overage: 500
```

---

## Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Immutable ledger** | Usage history cannot be tampered with |
| **Soft boundaries** | No hard blocks — service continues, overage tracked |
| **Injectable tiers** | Tier config is injectable, not hardcoded |
| **Audit-ready** | Immutable log = audit trail by default |

---

## What's Next?

| Topic | What You'll Learn |
|--------|-------------------|
| **[Interactive Playground](../playground/index.md)** | Test metering in browser |
| **API Reference: Metering** | Full API for MeteringLedger and TierManager |
| **Deployment** | Running metering in production |

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.