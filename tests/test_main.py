from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "app": "Terraform API",
        "status": "running",
        "version": "1.0.0"
    }