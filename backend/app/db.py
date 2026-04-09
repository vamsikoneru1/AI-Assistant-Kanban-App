import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def get_db_path() -> Path:
    env_path = os.getenv("PM_DB_PATH")
    if env_path:
        return Path(env_path)
    data_dir = Path(__file__).resolve().parent.parent / "data"
    if data_dir.exists():
        return data_dir / "pm.db"
    return Path(__file__).resolve().parent / "pm.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS columns (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                column_id TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE
            );
            CREATE UNIQUE INDEX IF NOT EXISTS columns_board_position
                ON columns (board_id, position);
            CREATE UNIQUE INDEX IF NOT EXISTS cards_column_position
                ON cards (column_id, position);
            """
        )


def ensure_user(conn: sqlite3.Connection, username: str) -> str:
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row:
        return row["id"]

    user_id = f"user-{uuid4().hex}"
    conn.execute(
        "INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, "password", now_iso()),
    )
    return user_id


def ensure_board(conn: sqlite3.Connection, user_id: str) -> str:
    row = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        board_id = row["id"]
    else:
        board_id = f"board-{uuid4().hex}"
        now = now_iso()
        conn.execute(
            "INSERT INTO boards (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (board_id, user_id, "My Board", now, now),
        )

    columns_count = conn.execute(
        "SELECT COUNT(*) AS count FROM columns WHERE board_id = ?", (board_id,)
    ).fetchone()["count"]
    if columns_count == 0:
        seed_board(conn, board_id)
    return board_id


def seed_board(conn: sqlite3.Connection, board_id: str) -> None:
    seed_columns = [
        ("col-backlog", "Backlog", ["card-1", "card-2"]),
        ("col-discovery", "Discovery", ["card-3"]),
        ("col-progress", "In Progress", ["card-4", "card-5"]),
        ("col-review", "Review", ["card-6"]),
        ("col-done", "Done", ["card-7", "card-8"]),
    ]
    seed_cards = {
        "card-1": ("Align roadmap themes", "Draft quarterly themes with impact statements and metrics."),
        "card-2": ("Gather customer signals", "Review support tags, sales notes, and churn feedback."),
        "card-3": ("Prototype analytics view", "Sketch initial dashboard layout and key drill-downs."),
        "card-4": ("Refine status language", "Standardize column labels and tone across the board."),
        "card-5": ("Design card layout", "Add hierarchy and spacing for scanning dense lists."),
        "card-6": ("QA micro-interactions", "Verify hover, focus, and loading states."),
        "card-7": ("Ship marketing page", "Final copy approved and asset pack delivered."),
        "card-8": ("Close onboarding sprint", "Document release notes and share internally."),
    }
    now = now_iso()

    for position, (column_id, title, _) in enumerate(seed_columns):
        conn.execute(
            "INSERT INTO columns (id, board_id, title, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (column_id, board_id, title, position, now, now),
        )

    for column_id, _, card_ids in seed_columns:
        for position, card_id in enumerate(card_ids):
            title, details = seed_cards[card_id]
            conn.execute(
                "INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (card_id, column_id, title, details, position, now, now),
            )


def load_board(conn: sqlite3.Connection, board_id: str) -> dict:
    columns = conn.execute(
        "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
        (board_id,),
    ).fetchall()
    if not columns:
        return {"columns": [], "cards": {}}

    column_ids = [column["id"] for column in columns]
    placeholders = ",".join("?" for _ in column_ids)
    cards = conn.execute(
        f"SELECT id, column_id, title, details FROM cards WHERE column_id IN ({placeholders}) ORDER BY column_id, position",
        column_ids,
    ).fetchall()

    cards_by_id: dict[str, dict] = {}
    cards_by_column = {column_id: [] for column_id in column_ids}
    for card in cards:
        cards_by_id[card["id"]] = {
            "id": card["id"],
            "title": card["title"],
            "details": card["details"],
        }
        cards_by_column[card["column_id"]].append(card["id"])

    columns_payload = [
        {
            "id": column["id"],
            "title": column["title"],
            "cardIds": cards_by_column.get(column["id"], []),
        }
        for column in columns
    ]

    return {"columns": columns_payload, "cards": cards_by_id}


def replace_board(conn: sqlite3.Connection, board_id: str, board: object) -> None:
    now = now_iso()
    conn.execute(
        "DELETE FROM cards WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?)",
        (board_id,),
    )
    conn.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

    for position, column in enumerate(board.columns):
        conn.execute(
            "INSERT INTO columns (id, board_id, title, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (column.id, board_id, column.title, position, now, now),
        )

    for column in board.columns:
        for position, card_id in enumerate(column.cardIds):
            card = board.cards[card_id]
            conn.execute(
                "INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (card.id, column.id, card.title, card.details, position, now, now),
            )

    conn.execute("UPDATE boards SET updated_at = ? WHERE id = ?", (now, board_id))


def create_column(conn: sqlite3.Connection, board_id: str, title: str) -> dict:
    column_id = f"col-{uuid4().hex}"
    now = now_iso()
    next_position = (
        conn.execute(
            "SELECT COALESCE(MAX(position), -1) AS max_pos FROM columns WHERE board_id = ?",
            (board_id,),
        ).fetchone()["max_pos"]
        + 1
    )
    conn.execute(
        "INSERT INTO columns (id, board_id, title, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (column_id, board_id, title, next_position, now, now),
    )
    return {"id": column_id, "title": title, "cardIds": []}


def update_column(conn: sqlite3.Connection, column_id: str, title: str) -> None:
    conn.execute(
        "UPDATE columns SET title = ?, updated_at = ? WHERE id = ?",
        (title, now_iso(), column_id),
    )


def delete_column(conn: sqlite3.Connection, column_id: str) -> None:
    conn.execute("DELETE FROM cards WHERE column_id = ?", (column_id,))
    conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))


def create_card(conn: sqlite3.Connection, column_id: str, title: str, details: str) -> dict:
    card_id = f"card-{uuid4().hex}"
    now = now_iso()
    next_position = (
        conn.execute(
            "SELECT COALESCE(MAX(position), -1) AS max_pos FROM cards WHERE column_id = ?",
            (column_id,),
        ).fetchone()["max_pos"]
        + 1
    )
    conn.execute(
        "INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (card_id, column_id, title, details, next_position, now, now),
    )
    return {"id": card_id, "title": title, "details": details}


def update_card(
    conn: sqlite3.Connection,
    card_id: str,
    title: Optional[str],
    details: Optional[str],
    column_id: Optional[str],
) -> None:
    updates: list[str] = []
    params: list[object] = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if details is not None:
        updates.append("details = ?")
        params.append(details)

    if column_id is not None:
        next_position = (
            conn.execute(
                "SELECT COALESCE(MAX(position), -1) AS max_pos FROM cards WHERE column_id = ?",
                (column_id,),
            ).fetchone()["max_pos"]
            + 1
        )
        updates.append("column_id = ?")
        params.append(column_id)
        updates.append("position = ?")
        params.append(next_position)

    if not updates:
        return

    updates.append("updated_at = ?")
    params.append(now_iso())
    params.append(card_id)

    conn.execute(
        f"UPDATE cards SET {', '.join(updates)} WHERE id = ?",
        params,
    )


def delete_card(conn: sqlite3.Connection, card_id: str) -> None:
    conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))


def get_board_id_for_username(conn: sqlite3.Connection, username: str) -> str:
    user_id = ensure_user(conn, username)
    return ensure_board(conn, user_id)


def column_belongs_to_board(conn: sqlite3.Connection, column_id: str, board_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM columns WHERE id = ? AND board_id = ?", (column_id, board_id)
    ).fetchone()
    return row is not None


def card_belongs_to_board(conn: sqlite3.Connection, card_id: str, board_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM cards JOIN columns ON cards.column_id = columns.id WHERE cards.id = ? AND columns.board_id = ?",
        (card_id, board_id),
    ).fetchone()
    return row is not None


def card_belongs_to_column(conn: sqlite3.Connection, card_id: str, column_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM cards WHERE id = ? AND column_id = ?",
        (card_id, column_id),
    ).fetchone()
    return row is not None


def columns_for_board(conn: sqlite3.Connection, board_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT id FROM columns WHERE board_id = ? ORDER BY position", (board_id,)
    ).fetchall()
    return [row["id"] for row in rows]


def cards_for_column(conn: sqlite3.Connection, column_id: str) -> Iterable[str]:
    rows = conn.execute(
        "SELECT id FROM cards WHERE column_id = ? ORDER BY position", (column_id,)
    ).fetchall()
    return [row["id"] for row in rows]
