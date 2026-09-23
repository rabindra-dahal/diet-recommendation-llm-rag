"""Module provisioning fast numpy-accelerated cosine similarity logic for custom recipes RAG."""

import json
import numpy as np
from backend_diet.db_core import get_db_connection


def save_recipe_to_knowledge_base(name: str, category: str, macros: str, ingredients: str, embedding: list[float]) -> None:
    """Persists a macro item summary block with its calculated vector coordinates into storage."""
    conn = get_db_connection()
    conn.cursor().execute(
        """INSERT INTO food_knowledge_base (recipe_name, category, macro_profile, ingredients, embedding_json) 
           VALUES (?, ?, ?, ?, ?)""",
        (str(name), category, macros, ingredients, json.dumps(list(embedding))),
    )
    conn.commit()
    conn.close()


def query_vector_store_rag(query_embedding: list[float], limit: int = 1) -> list[dict]:
    """Executes a low-latency numpy cosine-similarity fetch sweep across recipes."""
    conn = get_db_connection()
    rows = conn.cursor().execute(
        "SELECT recipe_name, category, macro_profile, ingredients, embedding_json FROM food_knowledge_base"
    ).fetchall()
    conn.close()

    if not rows or not query_embedding:
        return []

    q_vec = np.array(query_embedding)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []

    results = []
    for name, cat, macros, ing, emb_json in rows:
        if not emb_json:
            continue
        b_vec = np.array(json.loads(emb_json))
        b_norm = np.linalg.norm(b_vec)
        if b_norm == 0:
            continue

        similarity = np.dot(q_vec, b_vec) / (q_norm * b_norm)
        results.append(
            (
                similarity,
                {
                    "title": name,
                    "category": cat,
                    "macros": macros,
                    "ingredients": ing
                },
            )
        )

    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return mapping matching both precision matrix scoring and context values
    return [
        {
            "score": item[0],
            "title": item[1]["title"],
            "category": item[1]["category"],
            "macros": item[1]["macros"],
            "ingredients": item[1]["ingredients"]
        }
        for item in results[:limit]
    ]


def fetch_rag_document_inventory() -> list[dict]:
    """Extracts metadata summaries for all custom uploaded recipes inside the index."""
    conn = get_db_connection()
    rows = conn.cursor().execute(
        "SELECT id, recipe_name, category, macro_profile FROM food_knowledge_base ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "category": r[2], "summary": r[3]} for r in rows]


def delete_single_rag_document(doc_id: int) -> None:
    """Purges a specific recipe vector segment by its auto-increment key block ID."""
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM food_knowledge_base WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
