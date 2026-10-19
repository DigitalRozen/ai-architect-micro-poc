"""Helpers for tests that run against the live k3d cluster (make smoke)."""

import base64
import json
import subprocess
from dataclasses import dataclass

import pytest

NAMESPACE = "platform"
POD = "postgres-0"


def kubectl(*args: str) -> str:
    return subprocess.run(
        ["kubectl", "-n", NAMESPACE, *args], capture_output=True, text=True, check=True
    ).stdout


def read_secret(name: str) -> dict[str, str]:
    raw = json.loads(kubectl("get", "secret", name, "-o", "json"))["data"]
    return {key: base64.b64decode(value).decode() for key, value in raw.items()}


@dataclass
class SqlResult:
    ok: bool
    output: str


class Psql:
    """Runs SQL inside the postgres pod as a given role, over TCP so passwords are checked."""

    def __init__(self) -> None:
        secret = read_secret("postgres-credentials")
        self._passwords = {
            "ai_reader": secret["ai-reader-password"],
            "ai_writer": secret["ai-writer-password"],
            "postgres": secret["superuser-password"],
        }

    def run(self, role: str, sql: str) -> SqlResult:
        proc = subprocess.run(
            [
                "kubectl", "-n", NAMESPACE, "exec", "-i", POD, "--",
                "env", f"PGPASSWORD={self._passwords[role]}",
                "psql", "-h", "127.0.0.1", "-U", role, "-d", "erp",
                "-v", "ON_ERROR_STOP=1", "-tA",
            ],
            input=sql, capture_output=True, text=True,
        )  # fmt: skip
        return SqlResult(ok=proc.returncode == 0, output=(proc.stdout + proc.stderr).strip())


@pytest.fixture(scope="session")
def psql() -> Psql:
    return Psql()
