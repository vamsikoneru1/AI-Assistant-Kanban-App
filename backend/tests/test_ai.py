import json

from app import openrouter
from app.main import AIStructuredResponse


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeClient:
    def __init__(self, payload: dict):
        self.payload = payload
        self.last_request = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url: str, json: dict, headers: dict):
        self.last_request = {"url": url, "json": json, "headers": headers}
        return FakeResponse(self.payload)


def test_call_openrouter_extracts_content(monkeypatch):
    payload = {"choices": [{"message": {"content": "4"}}]}
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setattr(openrouter, "httpx", type("X", (), {"Client": lambda **_: FakeClient(payload)}))

    result = openrouter.call_openrouter("2+2")

    assert result == "4"


def test_structured_ai_endpoint_updates_board(client, monkeypatch):
    board = client.get("/api/board").json()
    board["columns"][0]["title"] = "AI Updated"

    response_payload = AIStructuredResponse(
        message="Updated the board.",
        updatedBoard=board,
    ).model_dump()
    monkeypatch.setattr(
        "app.main.call_openrouter_messages",
        lambda *args, **kwargs: json.dumps(response_payload),
    )

    response = client.post(
        "/api/ai/structured",
        json={
            "question": "Rename the first column",
            "board": board,
            "history": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["updated"] is True
    assert data["board"]["columns"][0]["title"] == "AI Updated"
