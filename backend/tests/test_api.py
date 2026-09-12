import pandas as pd
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_csv():
    csv = "Date,Region,Revenue\n2024-01-01,North,100\n2024-02-01,South,250\n2024-03-01,North,300\n"
    response = client.post(
        "/api/analyze",
        files={"file": ("sales.csv", csv, "text/csv")},
        data={"question": "Which region is performing best?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["overview"]["rows"] == 3
    assert body["key_metrics"]
    assert body["executive_summary"]
    assert isinstance(body["visualizations"], list)


def test_analyze_empty_file():
    response = client.post(
        "/api/analyze",
        files={"file": ("empty.csv", b"col\n", "text/csv")},
    )
    assert response.status_code == 400


def test_demo():
    response = client.post("/api/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["overview"]["rows"] > 0
    assert len(body["visualizations"]) >= 1
