from src.database import connect, load_series, save_series


def test_save_and_load_round_trip():
    conn = connect(":memory:")  # temporary database in RAM, nothing touches the disk
    save_series(conn, "cpi", "api-id", [("2017-02-01", 103.7), ("2017-01-01", 101.6)])
    assert load_series(conn, "cpi") == [("2017-01-01", 101.6), ("2017-02-01", 103.7)]


def test_saving_twice_does_not_duplicate():
    conn = connect(":memory:")
    rows = [("2017-01-01", 101.6)]
    save_series(conn, "cpi", "api-id", rows)
    save_series(conn, "cpi", "api-id", rows)
    assert load_series(conn, "cpi") == rows
