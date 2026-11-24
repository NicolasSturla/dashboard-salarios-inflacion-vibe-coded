"""Pure calculations on series: no API, no database, no screen. Easy to test.

A series is a list of (date, value) pairs, e.g. [("2017-01-01", 101.6), ...].
"""

Series = list[tuple[str, float]]


def rebase(series: Series, base_date: str) -> Series:
    """Rescale a series so it equals 100 on base_date.

    Index series from different sources start at different dates and bases
    (some wages are 100 in Oct-2015, CPI is 100 in Dec-2016). Rebasing them to
    the same date makes them comparable: 112 means "12% above the base month".
    """
    values = dict(series)
    if base_date not in values:
        raise ValueError(f"base date {base_date} is not in the series")
    base = values[base_date]
    return [(date, value / base * 100) for date, value in series]


def real_wage(wages: Series, cpi: Series, base_date: str) -> Series:
    """Purchasing power of wages, 100 = same as on base_date.

    real = (wage index / CPI), both rebased to base_date.
    Above 100: wages grew more than prices since base_date. Below 100: they lost.
    Only months present in BOTH series are used: wages are published ~2 months
    after CPI, and a month with only one of the two cannot be compared.
    """
    wages_rebased = dict(rebase(wages, base_date))
    cpi_rebased = dict(rebase(cpi, base_date))
    common = sorted(wages_rebased.keys() & cpi_rebased.keys())
    return [(date, wages_rebased[date] / cpi_rebased[date] * 100) for date in common]
