"""Module handling database connection layers to retain nutritional chat threads."""

from backend_diet.db_core import get_db_connection


def load_persisted_chat() -> list[dict]:
    """Loads chronological conversational blocks from internal historical rows."""
    conn = get_db_connection()
    rows = conn.cursor().execute(
        "SELECT role, content FROM chat_history ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]


def save_chat_message(role: str, content: str) -> None:
    """Stores text query segments securely to conversational logging tracks."""
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content)
    )
    conn.commit()
    conn.close()
