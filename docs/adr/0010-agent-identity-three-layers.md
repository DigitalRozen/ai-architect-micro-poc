# ADR-0010: Agent identity as three layers

- **Status:** Accepted
- **Date:** 2026-09-06
- **Note:** Carried over from an earlier docs-only version of this repo. It will be updated in Phase 7 to map each layer to the concrete components here.
- **Context:** Buyers ask who owns agents, what they can access, and what proof exists. Treating “agent identity” as one IAM product fails procurement and operations.

## Decision

Model agent identity as **three layers**, not one product:

1. **Human / org owner** — accountable person or team that can shut it down
2. **Workload / runtime identity** — how the agent authenticates to systems (service account, workload identity, short-lived credentials)
3. **Tool / data scope** — what the agent is allowed to read, write, spawn, and spend

Every agent component in this repo must name all three before tool selection.

## Consequences

- Vendor tools sit *under* the model; they do not replace it
- “We installed an NHI scanner” is not an architecture decision
- Audit evidence maps to layers (owner, credential lifecycle, scope diffs)

## Non-goals

- Picking a specific IAM/NHI vendor in this ADR
- Client-specific inventories
