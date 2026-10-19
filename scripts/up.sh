#!/usr/bin/env bash
# Create the local cluster (if needed), inject runtime secrets, deploy, and wait.
set -euo pipefail

CLUSTER=sovereign-agent
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for bin in docker k3d kubectl openssl curl; do
  command -v "$bin" >/dev/null || { echo "missing required tool: $bin" >&2; exit 1; }
done

if ! k3d cluster list "$CLUSTER" >/dev/null 2>&1; then
  k3d cluster create --config "$ROOT/deploy/k3d/cluster.yaml" --wait
fi
kubectl config use-context "k3d-$CLUSTER" >/dev/null

kubectl apply -f "$ROOT/deploy/base/namespaces.yaml"

# Secrets are generated on first run and live only in the cluster, never in git.
if ! kubectl -n platform get secret postgres-credentials >/dev/null 2>&1; then
  kubectl -n platform create secret generic postgres-credentials \
    --from-literal=superuser-password="$(openssl rand -hex 24)" \
    --from-literal=ai-reader-password="$(openssl rand -hex 24)" \
    --from-literal=ai-writer-password="$(openssl rand -hex 24)"
fi

if ! kubectl -n platform get secret keycloak-credentials >/dev/null 2>&1; then
  kubectl -n platform create secret generic keycloak-credentials \
    --from-literal=admin-password="$(openssl rand -hex 16)" \
    --from-literal=agent-ui-client-secret="$(openssl rand -hex 24)" \
    --from-literal=demo-password-alice="$(openssl rand -hex 6)" \
    --from-literal=demo-password-morgan="$(openssl rand -hex 6)" \
    --from-literal=demo-password-val="$(openssl rand -hex 6)"
fi

kubectl apply -k "$ROOT/deploy/base"
kubectl -n platform rollout status statefulset/postgres --timeout=180s
kubectl -n platform rollout status deployment/keycloak --timeout=300s

# Traefik is installed by k3s asynchronously; wait until the public URL answers.
for _ in $(seq 60); do
  curl -fsS -o /dev/null http://localhost:8080/auth/realms/kestrel && break
  sleep 2
done
curl -fsS -o /dev/null http://localhost:8080/auth/realms/kestrel \
  || { echo "Keycloak is not reachable on http://localhost:8080/auth" >&2; exit 1; }

echo "Cluster is up. Run 'make smoke' to verify, 'make creds' for demo logins."
