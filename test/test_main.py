# -*- coding: utf-8 -*-

from fastapi.testclient import TestClient


def test_read_main(client: TestClient):
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == True
