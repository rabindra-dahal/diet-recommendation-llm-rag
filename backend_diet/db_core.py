"""Database core framework provisioning baseline SQLite schemas for health profiles and food assets."""

import sqlite3

DB_FILE = "health_tracker.db"


def get_db_connection() -> sqlite3.Connection:
    """Returns a direct isolated connection instance handle to the health data asset."""
    return sqlite3.connect(DB_FILE)


def init_db() -> None:
    """Initializes schema tables for chat lines, weight trackers, meals, and food matrices."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS chat_history 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS health_goal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT UNIQUE, weight_target REAL
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS dynamic_food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE,
            calories INTEGER DEFAULT 0, entry_notes TEXT DEFAULT ''
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS food_knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT, recipe_name TEXT, category TEXT,
            macro_profile TEXT, ingredients TEXT, embedding_json TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS api_usage_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT, call_type TEXT, timestamp TEXT
        )"""
    )
    conn.commit()
    conn.close()
