"""Rilavo Protocol reference implementation (v0).

A stateless, cryptographically signed credential format that lets a receiving
system verify, without a network call and without learning anything beyond what
the credential discloses, that an agent holds a specific, time-boxed
authorization from a specific principal.

Implements the Rilavo Protocol Core Technical Specification:
  - Ed25519 signing only (P-11)
  - RFC 8785 (JCS) canonicalization before signing (P-11)
  - Audience-bound, exact-match action classes (P-07)
  - Proof-of-possession on every request (P-07)
  - Append-only hash-chained revocation log, fail-closed (P-09)
  - Key rotation with overlap window and retroactive compromise cutoff (P-12)
"""

__version__ = "0.1.0"
