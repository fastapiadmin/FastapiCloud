# -*- coding: utf-8 -*-

import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient

from app.main import create_app

app = create_app()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

