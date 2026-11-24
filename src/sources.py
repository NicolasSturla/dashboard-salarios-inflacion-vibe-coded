"""Download time series from the Argentine government API (datos.gob.ar)."""

import requests

API_URL = "https://apis.datos.gob.ar/series/api/series/"

# Series used by the dashboard: our short name -> official API id.
SERIES = {
    "cpi": "148.3_INIVELNAL_DICI_M_26",               # Consumer Price Index (IPC), base Dec-2016
    "wages_total": "149.1_TL_INDIIOS_OCTU_0_21",      # Wage index, total
    "wages_private_registered": "149.1_SOR_PRIADO_OCTU_0_25",
    "wages_private_unregistered": "149.1_SOR_PRIADO_OCTU_0_28",
    "wages_public": "149.1_SOR_PUBICO_OCTU_0_14",
    "wages_registered": "149.1_TL_REGIADO_OCTU_0_16",
}

# Months between the date a value is labelled with and the period it really measures.
# INDEC: the unregistered private-sector index comes from the household survey (EPH) and
# "tiene un rezago de cinco meses" (wage index press release / methodology N°16).
PUBLICATION_LAG_MONTHS = {"wages_private_unregistered": 5}


def fetch_series(series_id: str) -> list[tuple[str, float]]:
    """Return the full history of one series as a list of (date, value).

    Dates come as text in ISO format ("2017-01-01" = January 2017).
    """
    # The API returns 100 rows by default; 5000 is its maximum and covers decades of monthly data.
    params = {"ids": series_id, "limit": 5000, "format": "json"}
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()  # stop with a clear error if the API answered 4xx/5xx
    rows = response.json()["data"]  # e.g. [["2016-12-01", 100.0], ["2017-01-01", 101.5859], ...]

    # Missing data: the API sends None for a month it has no value for. Three options were considered:
    #   - Keep None: every later step (database, calculations, chart) would need to handle "no value".
    #   - Use 0:     wrong. 0 means "the index is zero", not "unknown", and real wage = wage / CPI
    #                would divide by zero or show a fake collapse in the chart.
    #   - Skip it:   chosen. The month simply does not exist in our data, which is the truth.
    # Similar cases handled elsewhere:
    #   - A series that comes back completely empty -> update_data.py warns and saves nothing.
    #   - CPI and wages ending in different months -> calculations must use only months present in both.
    return [(date, value) for date, value in rows if value is not None]


if __name__ == "__main__":
    # Quick manual check: python src/sources.py
    cpi = fetch_series(SERIES["cpi"])
    print(f"CPI: {len(cpi)} months, first {cpi[0]}, last {cpi[-1]}")
