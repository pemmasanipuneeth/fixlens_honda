"""Local Week 6 evaluation log."""

import sqlite3
from pathlib import Path

from .models import EvaluationRecord


DB_PATH = Path(__file__).resolve().parent.parent / "fixlens.db"


def initialize_database() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                attack_family TEXT NOT NULL,
                prompt TEXT NOT NULL,
                outcome TEXT NOT NULL,
                reasoning TEXT NOT NULL
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                year INTEGER NOT NULL,
                model TEXT NOT NULL,
                trim TEXT NOT NULL,
                engine TEXT NOT NULL,
                mileage INTEGER,
                vin_last6 TEXT,
                UNIQUE(nickname)
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_nickname TEXT NOT NULL,
                service TEXT NOT NULL,
                due_mileage INTEGER,
                notes TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )"""
        )


def save_evaluation(record: EvaluationRecord) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO evaluations (attack_family, prompt, outcome, reasoning) VALUES (?, ?, ?, ?)",
            (record.attack_family, record.prompt, record.outcome, record.reasoning),
        )


def evaluation_history() -> list[dict]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT created_at, attack_family, prompt, outcome, reasoning FROM evaluations ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def save_vehicle(nickname: str, year: int, model: str, trim: str, engine: str, mileage: int | None, vin_last6: str) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """INSERT INTO vehicles (nickname, year, model, trim, engine, mileage, vin_last6)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(nickname) DO UPDATE SET year=excluded.year, model=excluded.model,
               trim=excluded.trim, engine=excluded.engine, mileage=excluded.mileage,
               vin_last6=excluded.vin_last6""",
            (nickname, year, model, trim, engine, mileage, vin_last6[-6:]),
        )


def vehicle_history() -> list[dict]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT nickname, year, model, trim, engine, mileage, vin_last6 FROM vehicles ORDER BY nickname").fetchall()
    return [dict(row) for row in rows]


def save_reminder(vehicle_nickname: str, service: str, due_mileage: int | None, notes: str) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO reminders (vehicle_nickname, service, due_mileage, notes) VALUES (?, ?, ?, ?)",
            (vehicle_nickname, service, due_mileage, notes),
        )


def reminder_history() -> list[dict]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT vehicle_nickname, service, due_mileage, notes, completed FROM reminders ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

