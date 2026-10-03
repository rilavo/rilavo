"""Audit receipts (P-10).

A verifier logs, at minimum: which credential (by nonce hash — never full
contents), which issuer, the outcome, and a timestamp. The receipt binds to
the verified credential via a hash, so the verifier can later prove what it
checked without retaining the credential itself.
"""

from __future__ import annotations

import hashlib
import time


class ReceiptLog:
    def __init__(self) -> None:
        self.receipts: list[dict] = []

    def record(self, issuer: str, nonce: str, outcome: str, now: float | None = None) -> dict:
        receipt = {
            "iss": issuer,
            "credential_hash": hashlib.sha256(nonce.encode()).hexdigest(),
            "outcome": outcome,
            "ts": now if now is not None else time.time(),
        }
        self.receipts.append(receipt)
        return receipt
