import pytest

from src.calculations import real_wage, rebase


def test_rebase_sets_base_date_to_100():
    series = [("2017-01-01", 50.0), ("2017-02-01", 75.0)]
    assert rebase(series, "2017-01-01") == [("2017-01-01", 100.0), ("2017-02-01", 150.0)]


def test_rebase_rejects_missing_base_date():
    with pytest.raises(ValueError):
        rebase([("2017-01-01", 50.0)], "2020-01-01")


def test_wages_and_prices_growing_equally_keep_real_wage_at_100():
    wages = [("2017-01-01", 100.0), ("2017-02-01", 110.0)]
    cpi = [("2017-01-01", 200.0), ("2017-02-01", 220.0)]  # different base, same growth
    values = [value for _, value in real_wage(wages, cpi, "2017-01-01")]
    assert values == pytest.approx([100.0, 100.0])  # approx: decimals may differ by rounding


def test_prices_doubling_with_flat_wages_halves_real_wage():
    wages = [("2017-01-01", 100.0), ("2017-02-01", 100.0)]
    cpi = [("2017-01-01", 100.0), ("2017-02-01", 200.0)]
    assert real_wage(wages, cpi, "2017-01-01")[-1] == ("2017-02-01", 50.0)


def test_real_wage_uses_only_months_in_both_series():
    wages = [("2017-01-01", 100.0), ("2017-02-01", 105.0)]               # wages end earlier
    cpi = [("2017-01-01", 100.0), ("2017-02-01", 105.0), ("2017-03-01", 110.0)]
    assert [date for date, _ in real_wage(wages, cpi, "2017-01-01")] == ["2017-01-01", "2017-02-01"]
