"""Module calculating live macro metrics, user entry logs, and API transactions."""

from datetime import datetime
from backend_diet.db_core import get_db_connection


def increment_api_counter(call_type: str) -> None:
    """Increments telemetry count whenever a model utility network operation runs."""
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT INTO api_usage_telemetry (call_type, timestamp) VALUES (?, ?)",
        (call_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_total_api_calls() -> int:
    """Retrieves cumulative API operations executed across active workflows."""
    conn = get_db_connection()
    res = conn.cursor().execute("SELECT COUNT(*) FROM api_usage_telemetry").fetchone()
    conn.close()
    return res[0] if res else 0


def log_weight_target(weight_target: float) -> None:
    """Saves weight logging markers to map progression trend lines over charts."""
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT OR REPLACE INTO health_goal_logs (log_date, weight_target) VALUES (?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), weight_target),
    )
    conn.commit()
    conn.close()


def fetch_analytics_logs() -> list[tuple]:
    """Retrieves historical weight logging metrics sorted chronologically."""
    conn = get_db_connection()
    rows = conn.cursor().execute(
        "SELECT log_date, weight_target FROM health_goal_logs ORDER BY log_date ASC"
    ).fetchall()
    conn.close()
    return rows

def load_persisted_food_list() -> list[dict]:
    """Extracts custom logged meals securely using explicit index tuple unpacking."""
    conn = get_db_connection()
    # Explicitly pull all structural metrics columns
    rows = conn.cursor().execute(
        "SELECT id, item_name, calories, entry_notes FROM dynamic_food_log ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [
        {"id": f_id, "title": name, "calories": cals, "notes": notes}
        for f_id, name, cals, notes in rows
    ]

def save_food_item_to_list(food_name: str, calories: int, notes: str) -> None:
    """Saves a recommended meal along with pre-calculated macro parameters instantly."""
    conn = get_db_connection()
    # Write both name, parsed calories, and structured gram notes on initial collection click
    conn.cursor().execute(
        """INSERT OR REPLACE INTO dynamic_food_log (item_name, calories, entry_notes) 
           VALUES (?, ?, ?)""", 
        (food_name.strip(), calories, notes.strip())
    )
    conn.commit()
    conn.close()

def update_food_log_entry(food_name: str, calories: int, notes: str) -> None:
    """Updates specific calorie numbers and nutritional content notes on saved items."""
    conn = get_db_connection()
    conn.cursor().execute(
        "UPDATE dynamic_food_log SET calories = ?, entry_notes = ? WHERE item_name = ?",
        (calories, notes.strip(), food_name),
    )
    conn.commit()
    conn.close()


def delete_all_logged_foods() -> None:
    """Wipes all rows from the active user macro tracking database grid table."""
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM dynamic_food_log")
    conn.commit()
    conn.close()

""" Add Macro Accumulation Aggregations
    It parses the notes field using simple string matching to extract protein, 
    carb, and fat estimates (e.g., P:30g, C:45g, F:12g) from your saved foods.
"""
def fetch_kpi_summary_metrics() -> dict:
    """Calculates active summary telemetry across food, calories, and macronutrient profile splits."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rows = cursor.execute("SELECT calories, entry_notes FROM dynamic_food_log").fetchall()
    total_saved = len(rows)
    total_calories = sum([r[0] for r in rows if r[0] is not None])
    completed_reviews = len([r for r in rows if r[1] and str(r[1]).strip() != ""])
    
    # AUTOMATED ARRIVAL SWEEP: Extract macros without guessing or complex string splitting failures
    protein_total = 0
    carbs_total = 0
    fats_total = 0
    
    for _, notes in rows:
        if not notes:
            continue
        try:
            # Parses a clean, pre-structured context 'P:30g,C:10g,F:5g' perfectly
            parts = notes.replace(" ", "").split(",")
            for part in parts:
                if part.startswith("P:") and "g" in part:
                    protein_total += int(part.split("P:")[1].split("g")[0])
                elif part.startswith("C:") and "g" in part:
                    carbs_total += int(part.split("C:")[1].split("g")[0])
                elif part.startswith("F:") and "g" in part:
                    fats_total += int(part.split("F:")[1].split("g")[0])
        except Exception:
            continue  
            
    conn.close()
    return {
        "total_saved": total_saved,
        "total_calories": total_calories,
        "completed_reviews": completed_reviews,
        "protein": protein_total,
        "carbs": carbs_total,
        "fats": fats_total
    }


def clear_entire_session() -> None:
    """Flushes active chat lines, logged macros, and counter telemetry tables."""
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM chat_history")
    conn.cursor().execute("DELETE FROM dynamic_food_log")
    conn.cursor().execute("DELETE FROM api_usage_telemetry")
    conn.cursor().execute("DELETE FROM hydration_log")
    conn.commit()
    conn.close()

# (Add Water Ingestion Operations Hooks)
def log_water_intake(amount_ml: int) -> None:
    """Appends an incremental fluid volume record to the current calendar date."""
    conn = get_db_connection()
    current_date = datetime.now().strftime("%Y-%m-%d")
    conn.cursor().execute(
        "INSERT INTO hydration_log (log_date, amount_ml) VALUES (?, ?)",
        (current_date, amount_ml),
    )
    conn.commit()
    conn.close()


def get_daily_hydration_total() -> int:
    """Calculates the total water volume consumed on the current calendar date."""
    conn = get_db_connection()
    current_date = datetime.now().strftime("%Y-%m-%d")
    res = conn.cursor().execute(
        "SELECT SUM(amount_ml) FROM hydration_log WHERE log_date = ?", 
        (current_date,)
    ).fetchone()
    conn.close()
    return res if res and res is not None else 0

