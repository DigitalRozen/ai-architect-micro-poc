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
| 1 | k3d cluster, Postgres, synthetic ERP data | planned |
| 2 | Keycloak realm, users, roles | planned |
| 3 | LLM gateway with budgets and rate limits | planned |
| 4 | MCP ERP tool server with per-tool authorization | planned |
| 5 | Code sandbox on Kubernetes Jobs | planned |
| 6 | Agent, approval UI, audit, end-to-end scenario | planned |
| 7 | Architecture docs, ADRs, demo script | planned |

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
make sync   # install dev dependencies
make lint   # ruff check + format check
make test   # unit tests
```

## Docs

- [ADR-0010: Agent identity as three layers](docs/adr/0010-agent-identity-three-layers.md)
- [Agent governance checklist](docs/agent-governance-checklist.md)

## License

MIT (see `LICENSE`).
