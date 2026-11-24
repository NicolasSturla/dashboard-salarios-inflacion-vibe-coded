"""Download every series from the API and save it in data/datos.db.

Run by hand whenever new data is published:
    .\\.venv\\Scripts\\python.exe update_data.py
"""

from src.database import connect, save_series
from src.sources import SERIES, fetch_series


def main() -> None:
    conn = connect()
    for name, api_id in SERIES.items():
        rows = fetch_series(api_id)
        save_series(conn, name, api_id, rows)
        print(f"{name:28} {len(rows):4} months  {rows[0][0]} -> {rows[-1][0]}")
    conn.close()


if __name__ == "__main__":
    main()
