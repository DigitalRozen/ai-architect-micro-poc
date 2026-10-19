# Sovereign Agent Reference Architecture

A reference architecture for a **governed enterprise agent running on Kubernetes**, built to show how identity, an LLM gateway, tools, a code sandbox, human approval and audit fit together. It is designed so that security does not depend on trusting the LLM.

> **Status: work in progress.** This is a demo/reference architecture, **not production software**. It was built with AI-assisted coding. All company names and data are fictional and synthetic.

## Scenario (planned)

A buyer at a fictional aluminum-profile manufacturer asks an agent to prepare a purchase order for a material shortage. The agent:

1. reads inventory and open orders through an MCP tool server, using only a separate AI data layer;
2. runs an LLM-written quantity calculation inside an isolated, network-less Kubernetes Job;
3. drafts a purchase order that a procurement manager must approve (OIDC login) before anything is written;
4. leaves an append-only audit trail of every request, tool call, denial and approval.

A planted prompt injection in the ERP data tries to make the agent submit an inflated order. The demo shows it being blocked at the tool, database and approval layers.

## Planned components

| Concern | Component |
|---|---|
| Cluster | k3s (via k3d), single node |
| Identity | Keycloak (OIDC), roles enforced at gateway, tool and database layers |
| LLM gateway | LiteLLM: per-user keys, budgets, rate limits, spend logs; OpenRouter or a local mock model |
| Tools | Python MCP server over streamable HTTP |
| Sandbox | Ephemeral Kubernetes Job with deny-all egress NetworkPolicy |
| Data & audit | Postgres: core ERP schema, separate AI schema, append-only audit table |

## Build phases

| # | Phase | Status |
|---|---|---|
| 0 | Repo skeleton, lint, tests, CI, secret scanning | done |
| 1 | k3d cluster, Postgres, synthetic ERP data, CI smoke test on k3d | done |
| 2 | Keycloak realm, users, roles | done |
| 3 | LLM gateway with per-user keys, budgets, rate limits, spend attribution | done |
| 4 | MCP ERP tool server with per-tool authorization, draft policy, human approval endpoint | done |
| 5 | Code sandbox on Kubernetes Jobs | planned |
| 6 | Agent, approval UI, audit, end-to-end scenario | planned |
| 7 | Architecture docs, ADRs, demo script | planned |

## Quickstart

Requires Docker, [k3d](https://k3d.io) v5.8+, kubectl, openssl and [uv](https://docs.astral.sh/uv/).
Targets Linux and WSL2 (Ubuntu). CI runs `make up` and `make smoke` on an Ubuntu runner on every push.

```bash
cp .env.example .env   # optional for now; all values may stay empty
make sync              # install dev dependencies
make up                # create the k3d cluster and deploy
make smoke             # run tests against the live cluster
make down              # delete the cluster and its data
```

`make smoke` runs against the live cluster and currently proves:

| Layer | What is enforced | Tests |
|---|---|---|
| Database | AI roles cannot read or write the core `erp` schema; they can only create drafts in `ai`; only the approval role can create an ERP order; the audit log rejects updates and deletes | `tests/cluster/test_data_boundaries.py` |
| Identity | Signed tokens with the right issuer and `mcp-erp` audience, one role per user, the buyer cannot approve, the app client refuses the password grant | `tests/cluster/test_identity.py` |
| Tool server (MCP) | The server verifies the user's own token; roles map to tools; a deterministic draft policy rejects the planted injection; the model has no tool that places an order; approval needs the manager's token and rejects self-approval; every decision is audited | `tests/cluster/test_mcp_erp.py`, `services/mcp_erp/tests/` |
| LLM gateway | No key, no model; keys are bound to a user and a model allow-list; rate limits return 429; spent budgets block calls; spend is attributed per key | `tests/cluster/test_gateway.py` |

Without an `OPENROUTER_API_KEY` every model call goes to `scripted-llm`, a deterministic local model,
so the whole stack runs offline and in CI.

## Development

```bash
make lint   # ruff check + format check
make test   # unit tests (no cluster needed)
```

## Docs

- [ADR-0010: Agent identity as three layers](docs/adr/0010-agent-identity-three-layers.md)
- [Agent governance checklist](docs/agent-governance-checklist.md)

## License

MIT (see `LICENSE`).
