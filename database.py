import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


DB_PATH = Path("fitness.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    # Basic profile (single user for this simple app)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT,
            age INTEGER,
            gender TEXT CHECK (gender IN ('male', 'female')),
            height_cm REAL,
            activity_factor REAL DEFAULT 1.2
        )
        """
    )

    # Weight log
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weight_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            weight_kg REAL NOT NULL
        )
        """
    )

    # Food master table (simple built-in foods)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            protein_g REAL NOT NULL
        )
        """
    )

    # Food diary
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            meal_time TEXT,
            food_id INTEGER,
            quantity REAL DEFAULT 1.0,
            calories REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            protein_g REAL NOT NULL,
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
        """
    )

    # Exercise diary
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS exercise_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            exercise_type TEXT NOT NULL,
            category TEXT CHECK (category IN ('cardio', 'strength')) NOT NULL,
            duration_min REAL,   -- for cardio
            sets INTEGER,        -- for strength
            reps_per_set INTEGER,
            notes TEXT
        )
        """
    )

    conn.commit()

    # Seed a few common foods if table is empty
    cur.execute("SELECT COUNT(*) AS c FROM foods")
    count = cur.fetchone()["c"]
    if count == 0:
        seed_foods = [
            ("Grilled Chicken Breast (100g)", 165, 0, 3.6, 31),
            ("Brown Rice (1 cup cooked)", 216, 45, 1.8, 5),
            ("Apple (1 medium)", 95, 25, 0.3, 0.5),
            ("Banana (1 medium)", 105, 27, 0.3, 1.3),
            ("Oats (1/2 cup dry)", 150, 27, 3, 5),
            ("Whole Egg (1 large)", 72, 0.4, 4.8, 6.3),
        ]
        cur.executemany(
            "INSERT INTO foods (name, calories, carbs_g, fat_g, protein_g) VALUES (?, ?, ?, ?, ?)",
            seed_foods,
        )
        conn.commit()

    conn.close()


def upsert_profile(
    name: str,
    age: int,
    gender: str,
    height_cm: float,
    activity_factor: float,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM profile WHERE id = 1")
    exists = cur.fetchone()
    if exists:
        cur.execute(
            """
            UPDATE profile
            SET name = ?, age = ?, gender = ?, height_cm = ?, activity_factor = ?
            WHERE id = 1
            """,
            (name, age, gender, height_cm, activity_factor),
        )
    else:
        cur.execute(
            """
            INSERT INTO profile (id, name, age, gender, height_cm, activity_factor)
            VALUES (1, ?, ?, ?, ?, ?)
            """,
            (name, age, gender, height_cm, activity_factor),
        )
    conn.commit()
    conn.close()


def get_profile() -> Optional[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profile WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row


def add_weight_entry(log_date: str, weight_kg: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO weight_log (log_date, weight_kg) VALUES (?, ?)",
        (log_date, weight_kg),
    )
    conn.commit()
    conn.close()


def get_weight_entries() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM weight_log ORDER BY log_date")
    rows = cur.fetchall()
    conn.close()
    return rows


def search_foods(query: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{query.lower()}%"
    cur.execute(
        "SELECT * FROM foods WHERE LOWER(name) LIKE ? ORDER BY name LIMIT 50", (q,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def add_food_log(
    log_date: str,
    meal_time: str,
    base_food: Optional[sqlite3.Row],
    quantity: float,
    calories: float,
    carbs_g: float,
    fat_g: float,
    protein_g: float,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    food_id = base_food["id"] if base_food is not None else None
    cur.execute(
        """
        INSERT INTO food_log
        (log_date, meal_time, food_id, quantity, calories, carbs_g, fat_g, protein_g)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (log_date, meal_time, food_id, quantity, calories, carbs_g, fat_g, protein_g),
    )
    conn.commit()
    conn.close()


def get_food_logs_by_date(log_date: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT fl.*, f.name AS food_name
        FROM food_log fl
        LEFT JOIN foods f ON fl.food_id = f.id
        WHERE fl.log_date = ?
        ORDER BY fl.id
        """,
        (log_date,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def add_exercise_log(
    log_date: str,
    exercise_type: str,
    category: str,
    duration_min: Optional[float],
    sets: Optional[int],
    reps_per_set: Optional[int],
    notes: str,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO exercise_log
        (log_date, exercise_type, category, duration_min, sets, reps_per_set, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (log_date, exercise_type, category, duration_min, sets, reps_per_set, notes),
    )
    conn.commit()
    conn.close()


def get_exercise_logs_by_date(log_date: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM exercise_log
        WHERE log_date = ?
        ORDER BY id
        """,
        (log_date,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_daily_nutrient_totals(log_date: str) -> Dict[str, float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            SUM(calories) AS calories,
            SUM(carbs_g) AS carbs_g,
            SUM(fat_g) AS fat_g,
            SUM(protein_g) AS protein_g
        FROM food_log
        WHERE log_date = ?
        """,
        (log_date,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return {"calories": 0, "carbs_g": 0, "fat_g": 0, "protein_g": 0}
    return {k: row[k] or 0 for k in row.keys()}



