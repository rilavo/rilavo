# Rilavo Product — Customer Segments (E-04)

**Tree:** Product
**Wave:** 1 — System Foundation
**Status:** Decided (segments 1–2); Working assumption (segments 3–4)
**Depends on:** E-03
**Closes when:** Each segment closes independently, as real pilots land in it — this document does not wait for all four to be proven before segments 1–2 are treated as decided.

## Segments, ranked by buying urgency — not by market size

**1. API and platform providers with active, unmanaged agent traffic today.** The sharpest, most immediate fit — the problem in E-03 is already happening to them, not hypothetical.

**2. MCP server operators specifically.** A distinct, addressable sub-segment within (1), made concrete by the documented authentication gap: independent measurements put roughly 38–40% of exposed MCP servers running with no declared authentication at all, and dynamic testing found the real enforcement gap far worse. This is a segment defined by a checkable, current fact, not a persona built from assumption.

**3. Fintech and marketplace platforms with agent-initiated transactions.** A reasonable extension of the same underlying problem into a higher-stakes transaction context.

**4. Compliance-heavy verticals, once Horizon 3 ships.** Not addressable yet — this segment doesn't exist as a real buyer until content-provenance or human-verification products (E-10) are actually built.

## Why 1–2 are marked Decided and 3–4 are not

Segments 1 and 2 are supported by the same wedge evidence already established in the Protocol tree (P-01, P-03) — a real, current, measured gap. Segments 3 and 4 are informed projection: reasonable extrapolations of where the same underlying problem likely recurs, but without equivalent independent evidence yet. Marking them with the same confidence as 1–2 would be exactly the kind of manufactured certainty this project has consistently avoided elsewhere; there's no reason to relax that discipline here just because it's a commercial document rather than a technical one.

## What changes segment 3 or 4 from "working assumption" to "decided"

Not more analysis. A real pilot customer in that segment, converting on the same terms segments 1–2 already have.
