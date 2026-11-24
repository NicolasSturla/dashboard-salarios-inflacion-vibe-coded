"""Store and read the series in a local SQLite database (data/datos.db)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "datos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS series (
    name   TEXT PRIMARY KEY,   -- our short name, e.g. 'cpi'
    api_id TEXT NOT NULL       -- official id in the datos.gob.ar API
);
CREATE TABLE IF NOT EXISTS observations (
    series_name TEXT NOT NULL REFERENCES series(name),
    date        TEXT NOT NULL,  -- ISO date, first day of the month: '2017-01-01'
    value       REAL NOT NULL,  -- months without data are skipped upstream, never stored as NULL or 0
    PRIMARY KEY (series_name, date)
);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Open the database (creating the file and tables if missing)."""
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def save_series(conn: sqlite3.Connection, name: str, api_id: str,
                rows: list[tuple[str, float]]) -> None:
    """Insert or update one series and all its observations, in one transaction."""
    with conn:  # commits if everything works, rolls back if anything fails
        conn.execute("INSERT OR REPLACE INTO series (name, api_id) VALUES (?, ?)", (name, api_id))
        conn.executemany(
            "INSERT OR REPLACE INTO observations (series_name, date, value) VALUES (?, ?, ?)",
            [(name, date, value) for date, value in rows],
        )


def load_series(conn: sqlite3.Connection, name: str) -> list[tuple[str, float]]:
    """Return one series as (date, value) pairs, oldest first."""
    cursor = conn.execute(
        "SELECT date, value FROM observations WHERE series_name = ? ORDER BY date", (name,)
    )
    return cursor.fetchall()
