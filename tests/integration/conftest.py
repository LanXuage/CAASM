#!/bin/env python3
"""
Integration test fixtures using testcontainers and docker-compose.

Provides:
- Redis container via testcontainers
- Kafka container via testcontainers
- Nebula Graph cluster via docker-compose (no Python testcontainers module available)
"""

import os
import sys
import time
import pytest
import subprocess
from typing import Generator

# Docker compose project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def is_docker_available() -> bool:
    """Check if Docker is available for integration tests."""
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


# ========== Redis fixtures (testcontainers) ==========


@pytest.fixture(scope="session")
def redis_container():
    """Session-scoped Redis container via testcontainers."""
    if not is_docker_available():
        pytest.skip("Docker not available")

    from testcontainers.redis import RedisContainer

    container = RedisContainer("redis:7.4.0")
    container.start()
    yield container
    container.stop()


@pytest.fixture
def redis_client(redis_container):
    """Get a Redis client connected to the test container."""
    return redis_container.get_client()


# ========== Kafka fixtures (testcontainers) ==========


@pytest.fixture(scope="session")
def kafka_container():
    """Session-scoped Kafka container via testcontainers."""
    if not is_docker_available():
        pytest.skip("Docker not available")

    from testcontainers.kafka import KafkaContainer

    container = KafkaContainer("apache/kafka:3.8.0")
    container.start()
    yield container
    container.stop()


@pytest.fixture
def kafka_bootstrap_servers(kafka_container):
    """Get Kafka bootstrap servers string."""
    return kafka_container.get_bootstrap_server()


# ========== Nebula Graph fixtures (docker-compose based) ==========


@pytest.fixture(scope="session")
def nebula_cluster():
    """
    Session-scoped Nebula Graph cluster.

    Uses the project's docker-compose to start a Nebula cluster.
    This is used because testcontainers-python has no Nebula module.
    """
    if not is_docker_available():
        pytest.skip("Docker not available")

    compose_file = os.path.join(PROJECT_ROOT, "compose.yml")

    # Check if Nebula services are already running
    check = subprocess.run(
        ["docker", "compose", "-f", compose_file, "--profile", "dev",
         "ps", "graphd-dev", "--format", "json"],
        capture_output=True, text=True,
    )

    already_running = False
    if check.returncode == 0 and check.stdout.strip():
        import json
        try:
            services = json.loads(check.stdout)
            already_running = any(
                s.get("State") == "running" for s in services
                if isinstance(s, dict)
            )
        except json.JSONDecodeError:
            pass

    if not already_running:
        # Start Nebula infrastructure
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "--profile", "dev",
             "up", "-d", "metad-dev", "storaged-dev", "graphd-dev"],
            capture_output=True, check=True,
        )
        # Wait for cluster to be ready
        time.sleep(30)

    # Connection info
    nebula_config = {
        "host": "localhost",
        "port": 9669,
        "username": "root",
        "password": "nebula",
        "space": "caasm",
    }

    yield nebula_config

    # Don't tear down - keep cluster running for subsequent test runs


@pytest.fixture
def nebula_facade(nebula_cluster):
    """Get a NebulaFacade connected to the test cluster."""
    from shared.nebula import NebulaFacade

    facade = NebulaFacade(
        nebula_cluster["username"],
        nebula_cluster["password"],
        nebula_cluster["space"],
        [(nebula_cluster["host"], nebula_cluster["port"])],
    )
    yield facade
    facade.close()