"""Contract verification tests for docs/openapi.json (Room 6 API contract)."""

import json
from pathlib import Path


def test_openapi_contract_validity(repo_root: Path) -> None:
    """Verify docs/openapi.json exists, is valid JSON, and adheres to OpenAPI 3.0."""
    openapi_path = repo_root / "docs" / "openapi.json"
    assert openapi_path.exists(), f"Missing OpenAPI contract file at {openapi_path}"

    content = openapi_path.read_text(encoding="utf-8")
    data = json.loads(content)

    assert "openapi" in data, "Missing openapi version key"
    assert data["openapi"].startswith("3."), f"Expected OpenAPI 3.x, got {data['openapi']}"
    assert "paths" in data, "Missing paths section in openapi.json"

    expected_endpoints = [
        "/api/v1/health",
        "/api/v1/plants",
        "/api/v1/plants/{id}/forecast",
        "/api/v1/plants/{id}/measurements",
        "/api/v1/plants/{id}/health",
        "/api/v1/plants/{id}/alerts",
        "/api/v1/plants/{id}/model-health",
    ]

    for endpoint in expected_endpoints:
        assert endpoint in data["paths"], f"Missing required analytical endpoint in contract: {endpoint}"

    # Verify that measurements endpoint supports both GET and POST
    measurements_ops = data["paths"]["/api/v1/plants/{id}/measurements"]
    assert "get" in measurements_ops, "Missing GET operation on measurements endpoint"
    assert "post" in measurements_ops, "Missing POST operation on measurements endpoint"
