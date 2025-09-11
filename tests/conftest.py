from fastapi.testclient import TestClient
from fastapi_zero.app import app

client = TestClient(app)
