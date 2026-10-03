# Rilavo Protocol — Protocol Licensing (P-39)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** None
**Closes when:** Locked at first public code release — a license, unlike most decisions in this project, is very expensive to change after the fact, so this one is treated as effectively permanent once exercised.

## The decision

The reference implementation and SDKs are licensed permissively — Apache 2.0 or MIT — not copyleft.

## The correction this document exists to make explicit

Earlier project material floated a copyleft license, specifically GPLv3, as a deliberate "anti-fork trap" — the theory being that a competitor forking the protocol would be legally compelled to open-source their own modifications. That reasoning does not survive scrutiny. GPLv3's copyleft obligation triggers on *distribution* of a derivative work. A well-resourced competitor that forks the code and runs a modified version purely as an internal hosted service never distributes anything, and therefore never has to release a single line back — this exact gap is why the AGPL exists, and even AGPL's network-use clause is slow and legally contested to enforce against an opponent with more lawyers than a young protocol project has. A license clause was never going to stop a determined forker. A network they'd have to rebuild from zero does that instead.

## The second reason, not just the correction

Copyleft licensing creates real adoption friction for the exact audience this protocol most needs as verifiers: many products carry blanket policies against GPL-family code in commercial products, independent of how the license would actually apply to their specific use. A licensing choice that quietly narrows the pool of willing verifiers works against the protocol's entire purpose, which depends on verifiers adopting it without friction.

## Where the actual moat lives instead

Correctly identified elsewhere, not invented here: issuer reputation, accumulated fraud-pattern intelligence, an installed base of verifiers who already trust the format, and standing with standards bodies. A permissive license gives away none of that — none of it is in the codebase. A restrictive license would have failed to protect any of it either, since none of it depends on what the license says.

## Status

**Rejected:** copyleft (GPLv3 or AGPL) as the anti-fork mechanism.
**Decided:** permissive licensing (Apache 2.0 or MIT) for the reference implementation and SDKs.
