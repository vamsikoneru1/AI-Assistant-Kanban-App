import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db
from app.openrouter import call_openrouter, call_openrouter_messages

app = FastAPI()


class CardPayload(BaseModel):
    id: str
    title: str
    details: str


class ColumnPayload(BaseModel):
    id: str
    title: str
    cardIds: list[str] = Field(default_factory=list)


class BoardPayload(BaseModel):
    columns: list[ColumnPayload]
    cards: dict[str, CardPayload]


class ColumnCreate(BaseModel):
    title: str


class ColumnUpdate(BaseModel):
    title: Optional[str] = None


class CardCreate(BaseModel):
    column_id: str
    title: str
    details: str = "No details yet."


class CardUpdate(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None
    column_id: Optional[str] = None


class AIPrompt(BaseModel):
    prompt: Optional[str] = None


class AIHistoryItem(BaseModel):
    role: str
    content: str


class AIStructuredRequest(BaseModel):
    question: str
    board: BoardPayload
    history: list[AIHistoryItem] = Field(default_factory=list)


class AIStructuredResponse(BaseModel):
    message: str
    updatedBoard: Optional[BoardPayload] = None


@app.on_event("startup")
def on_startup() -> None:
    db.init_db()


@app.get("/api/health")
def read_health() -> dict:
    return {"status": "ok", "message": "hello from fastapi"}


@app.post("/api/ai")
def call_ai(payload: AIPrompt) -> dict:
    prompt = payload.prompt or "2+2"
    try:
        response = call_openrouter(prompt)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter request failed",
        ) from exc
    return {"prompt": prompt, "response": response}


@app.post("/api/ai/structured")
def call_ai_structured(payload: AIStructuredRequest, username: str = "user") -> dict:
    response_schema = AIStructuredResponse.model_json_schema()
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "kanban_response",
            "schema": response_schema,
            "strict": True,
        },
    }

    system_prompt = (
        "You are a helpful assistant for a Kanban board. "
        "Always respond with JSON that matches the provided schema. "
        "Only include updatedBoard when you intend to change the board."
    )
    board_json = json.dumps(payload.board.model_dump())
    user_prompt = (
        "Question:\n"
        f"{payload.question}\n\n"
        "Board JSON:\n"
        f"{board_json}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for item in payload.history:
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": user_prompt})

    try:
        content = call_openrouter_messages(messages, response_format=response_format)
        parsed = json.loads(content)
        structured = AIStructuredResponse.model_validate(parsed)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter structured response failed",
        ) from exc

    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        updated_board = structured.updatedBoard
        if updated_board is not None:
            db.replace_board(conn, board_id, updated_board)
            updated_payload = db.load_board(conn, board_id)
        else:
            updated_payload = db.load_board(conn, board_id)

    return {
        "message": structured.message,
        "updated": updated_board is not None,
        "board": updated_payload,
    }


@app.get("/api/board")
def get_board(username: str = "user") -> dict:
    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        return db.load_board(conn, board_id)


@app.put("/api/board")
def put_board(payload: BoardPayload, username: str = "user") -> dict:
    column_ids = [column.id for column in payload.columns]
    if len(column_ids) != len(set(column_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate column ids")

    referenced_cards = [card_id for column in payload.columns for card_id in column.cardIds]
    if len(referenced_cards) != len(set(referenced_cards)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate card ids")

    if set(referenced_cards) != set(payload.cards.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card ids must match referenced cards",
        )

    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        db.replace_board(conn, board_id, payload)
        return db.load_board(conn, board_id)


@app.post("/api/columns")
def create_column(payload: ColumnCreate, username: str = "user") -> dict:
    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        return db.create_column(conn, board_id, payload.title)


@app.patch("/api/columns/{column_id}")
def update_column(column_id: str, payload: ColumnUpdate, username: str = "user") -> dict:
    if payload.title is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")

    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        if not db.column_belongs_to_board(conn, column_id, board_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        db.update_column(conn, column_id, payload.title)
        return {"id": column_id, "title": payload.title}


@app.delete("/api/columns/{column_id}")
def delete_column(column_id: str, username: str = "user") -> dict:
    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        if not db.column_belongs_to_board(conn, column_id, board_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        db.delete_column(conn, column_id)
        return {"status": "deleted"}


@app.post("/api/cards")
def create_card(payload: CardCreate, username: str = "user") -> dict:
    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        if not db.column_belongs_to_board(conn, payload.column_id, board_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        return db.create_card(conn, payload.column_id, payload.title, payload.details)


@app.patch("/api/cards/{card_id}")
def update_card(card_id: str, payload: CardUpdate, username: str = "user") -> dict:
    if payload.title is None and payload.details is None and payload.column_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")

    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        if not db.card_belongs_to_board(conn, card_id, board_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

        if payload.column_id is not None and not db.column_belongs_to_board(
            conn, payload.column_id, board_id
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")

        db.update_card(conn, card_id, payload.title, payload.details, payload.column_id)
        return {"status": "updated"}


@app.delete("/api/cards/{card_id}")
def delete_card(card_id: str, username: str = "user") -> dict:
    with db.get_connection() as conn:
        board_id = db.get_board_id_for_username(conn, username)
        if not db.card_belongs_to_board(conn, card_id, board_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        db.delete_card(conn, card_id)
        return {"status": "deleted"}


static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
