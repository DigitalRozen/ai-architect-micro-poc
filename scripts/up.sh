#!/usr/bin/env bash
# Create the local cluster (if needed), inject runtime secrets, deploy, and wait.
set -euo pipefail

CLUSTER=sovereign-agent
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for bin in docker k3d kubectl openssl; do
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

kubectl apply -k "$ROOT/deploy/base"
kubectl -n platform rollout status statefulset/postgres --timeout=180s

echo "Cluster is up. Run 'make smoke' to verify."
