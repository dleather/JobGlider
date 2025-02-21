import json
import pytest

def test_home_route(client):
    """Test that the home route returns the expected greeting."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, Flask!" in response.data

def test_webhook_success(client):
    """
    Test that a valid POST request to /webhook triggers the full workflow
    and returns a success status with the dummy Windows folder path.
    """
    payload = {
        "Job URL": "http://dummy.url",
        "ID": "dummy_id"
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["documents_folder"] == "C:/dummy/windows_folder"

def test_webhook_error(client, monkeypatch):
    """
    Test that if one of the internal functions (e.g. extract_job_details)
    raises an Exception, the /webhook endpoint returns an error status.
    """
    def raise_error(url):
        raise Exception("Test error")
    monkeypatch.setattr(
        "src.server.webhook_server.extract_job_details", 
        raise_error
    )
    payload = {
        "Job URL": "http://dummy.url",
        "ID": "dummy_id"
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert "Test error" in data["message"]
