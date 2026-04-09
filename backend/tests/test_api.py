def test_get_board(client):
    response = client.get("/api/board")
    assert response.status_code == 200
    data = response.json()
    assert len(data["columns"]) == 5
    assert "cards" in data


def test_add_column(client):
    response = client.post("/api/columns", json={"title": "New Column"})
    assert response.status_code == 200
    column_id = response.json()["id"]

    board = client.get("/api/board").json()
    assert any(column["id"] == column_id for column in board["columns"])


def test_add_card(client):
    board = client.get("/api/board").json()
    column_id = board["columns"][0]["id"]

    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Test card", "details": "Notes"},
    )
    assert response.status_code == 200
    card_id = response.json()["id"]

    board = client.get("/api/board").json()
    assert card_id in board["cards"]


def test_put_board(client):
    board = client.get("/api/board").json()
    board["columns"][0]["title"] = "Updated"

    response = client.put("/api/board", json=board)
    assert response.status_code == 200
    updated = response.json()
    assert updated["columns"][0]["title"] == "Updated"
