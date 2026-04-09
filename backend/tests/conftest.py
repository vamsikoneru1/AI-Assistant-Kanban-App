import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
