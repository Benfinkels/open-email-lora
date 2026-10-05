from fastapi.testclient import TestClient
from unittest.mock import patch
from runtime.api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data


def test_info_endpoint():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "endpoint" in data


def test_classify_endpoint_mocked():
    fake_ollama_resp = {
        "response": "ACTION\nThis email requires urgent attention."
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = fake_ollama_resp

        payload = {
            "sender": "boss@corp.com",
            "subject": "Review Q3 numbers",
            "body": "Need your approval today."
        }
        response = client.post("/classify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == "ACTION"
        assert data["confidence"] > 0
