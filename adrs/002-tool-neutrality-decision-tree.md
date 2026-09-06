# ADR-002: Tool-neutrality decision tree

- **Status:** Accepted
- **Date:** 2026-09-06
- **Context:** Enterprises burn cycles on PoCs that were tool-first. Lock-in shows up before the decision is clear.

## Decision

Before any tool shortlist, answer in order:

1. **What decision must this PoC unlock?** (one sentence, CEO-readable)
2. **What constraint is binding?** (identity, data residency, latency, cost, change risk)
3. **What would falsify success in ≤3 weeks?**
4. **Which interfaces must stay portable?** (API contracts, event shapes, identity model)
5. **Only then:** which tools can prove the decision without owning the architecture

If step 1–4 are unclear, stop. Do not start a vendor PoC.

## Consequences

- Micro-PoCs ship a decision memo + evidence, not a preferred stack
- Tool swaps later are cheaper because interfaces were named first
- Sales conversations stay architecture-led

## Anti-patterns

- Leading with model or platform logos
- “We’ll pick the model first”
- Success defined only as “demo impressed the room”
