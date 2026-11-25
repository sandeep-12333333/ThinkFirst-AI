import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path(__file__).resolve().parent.parent / "thinkfirst.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                reasoning_score REAL,
                confidence_signal TEXT,
                confidence_rating REAL,
                is_challenge INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS learning_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                reasoning_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


def ensure_student(student_name: str) -> None:
    init_database()
    with get_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO students (name) VALUES (?)",
            (student_name.strip() or "Student",),
        )


def save_attempt(
    student_name: str,
    topic: str,
    question: str,
    reasoning: str,
    reasoning_score: float,
    confidence_signal: str,
    confidence_rating: Optional[float] = None,
    is_challenge: bool = False,
) -> int:
    ensure_student(student_name)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO attempts
                (student_name, topic, question, reasoning, reasoning_score,
                 confidence_signal, confidence_rating, is_challenge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_name,
                topic,
                question,
                reasoning,
                reasoning_score,
                confidence_signal,
                confidence_rating,
                int(is_challenge),
            ),
        )
        return int(cursor.lastrowid)


def save_event(
    student_name: str,
    event_type: str,
    details: str,
    reasoning_score: Optional[float] = None,
) -> None:
    ensure_student(student_name)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO learning_events
                (student_name, event_type, details, reasoning_score)
            VALUES (?, ?, ?, ?)
            """,
            (student_name, event_type, details, reasoning_score),
        )


def get_attempts(student_name: str, limit: int = 200) -> List[Dict[str, Any]]:
    ensure_student(student_name)
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM attempts
            WHERE student_name = ?
            ORDER BY created_at ASC, id ASC
            LIMIT ?
            """,
            (student_name, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_events(student_name: str, limit: int = 500) -> List[Dict[str, Any]]:
    ensure_student(student_name)
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM learning_events
            WHERE student_name = ?
            ORDER BY created_at ASC, id ASC
            LIMIT ?
            """,
            (student_name, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_reasoning_history(student_name: str) -> List[Dict[str, Any]]:
    return get_attempts(student_name)
