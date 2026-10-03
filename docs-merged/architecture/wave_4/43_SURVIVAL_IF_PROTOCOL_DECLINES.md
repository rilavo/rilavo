# Rilavo Product — Survival If Rilavo Protocol Declines (E-43)

**Tree:** Product
**Wave:** 4 — Survival & Defensibility
**Status:** **Open — the least resolved item in the entire project.** That status doesn't change here. What changes is how precisely the discomfort is examined, rather than restated once more and left alone.
**Depends on:** E-26
**Closes when:** Only through real operation — and possibly never fully, if the scenario never resolves cleanly one way or the other.

## The scenario, stated without softening

A different standard — descended from CIMD, ID-JAG, AAuth, Biscuit, AIP, or something not yet named (P-18) — achieves meaningfully wider adoption than Rilavo's credential format. Or a dominant ecosystem Rilavo's wedge depends on, MCP or a major agent framework, officially adopts a different default rather than Rilavo's. Rilavo the protocol becomes a minority format. What happens to Rilavo Product, which built its entire commercial layer on top of it?

## Early signals worth watching, named specifically rather than left vague

A competing standard achieving materially higher *verifier* adoption specifically — not issuer adoption, since a format is only as useful as how many verifiers will accept it, and verifier count is the more load-bearing metric to track (P-18's own interoperability posture already implies this, but it's worth stating as an explicit monitored signal here rather than leaving it implicit). A major agent framework or MCP itself publishing a different format as its recommended or default authorization mechanism. Standards bodies converging around a competing spec rather than Rilavo's.

## The honest breakdown Product's fallback actually depends on

Not a comforting assertion that "operating skill transfers." An actual breakdown of what does and doesn't:

**Likely transfers, genuinely protocol-agnostic:** the fraud-abuse *patterns* themselves — velocity anomalies, credential-reuse signatures, the general shape of authorization abuse — don't depend on which credential format carries them. Compliance packaging and jurisdiction-mapping work (E-10) is similarly format-agnostic; a compliance product mostly cares about what was verified and when, not the specific wire format used to verify it. Operational discipline — uptime engineering, incident response, key custody practices — transfers directly regardless of which protocol sits underneath it.

**Does not transfer:** the specific credential-format expertise itself, and every integration built specifically against Rilavo's exact API and SDK (P-19, P-20). A customer integrated against Rilavo's format doesn't automatically become a customer of whatever format wins instead — that relationship would need to be rebuilt, not carried over.

**Genuinely unknown:** whether the transferable assets are commercially sufficient on their own, sold against a different underlying protocol, to sustain a business — or whether Rilavo Product's actual value, in customers' eyes, has always been "the company that made *this specific* format usable," in which case the transferable assets are real but insufficient alone.

## Why this document doesn't try to resolve that last uncertainty

Because doing so would require inventing an answer this project has no evidence for yet. The honest position, consistent with every other Open item in this wave, is that this is a real, live risk with a partially-favorable and partially-unfavorable answer already visible in the breakdown above — and the rest genuinely depends on how the market actually moves, which hasn't happened yet.

## What would change this document

Real evidence of a competing standard's adoption trajectory, tracked against the verifier-count signal named above — and, if that trajectory becomes serious, a real test of whether the "transfers / doesn't transfer" breakdown above holds when Product actually has to act on it, not just describe it.
