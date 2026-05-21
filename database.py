import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "recipes.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_recipes_table() -> None:
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                prep_time INTEGER,
                cook_time INTEGER,
                servings INTEGER,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                image_filename TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)
        connection.commit()
    finally:
        connection.close()


def add_recipe(
    title: str,
    category: str,
    prep_time: str,
    cook_time: str,
    servings: str,
    ingredients: str,
    instructions: str,
) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO recipes (
                title,
                category,
                prep_time,
                cook_time,
                servings,
                ingredients,
                instructions
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                category,
                prep_time or None,
                cook_time or None,
                servings or None,
                ingredients,
                instructions,
            ),
        )
        connection.commit()
    finally:
        connection.close()


def get_all_recipes() -> list[sqlite3.Row]:
    connection = get_connection()

    try:
        recipes = connection.execute("""
            SELECT
                id,
                title,
                category,
                prep_time,
                cook_time,
                servings,
                ingredients,
                instructions,
                image_filename,
                created_at
            FROM recipes
            ORDER BY created_at DESC, id DESC
            """).fetchall()

        return recipes
    finally:
        connection.close()
