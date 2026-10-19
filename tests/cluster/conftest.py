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


@dataclass
class SqlResult:
    ok: bool
    output: str


class Psql:
    """Runs SQL inside the postgres pod as a given role, over TCP so passwords are checked."""

    def __init__(self) -> None:
        raw = json.loads(kubectl("get", "secret", "postgres-credentials", "-o", "json"))["data"]
        self._passwords = {
            "ai_reader": base64.b64decode(raw["ai-reader-password"]).decode(),
            "ai_writer": base64.b64decode(raw["ai-writer-password"]).decode(),
            "postgres": base64.b64decode(raw["superuser-password"]).decode(),
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
