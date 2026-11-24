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


def fetch_series(series_id: str) -> list[tuple[str, float]]:
    """Return the full history of one series as a list of (date, value).

    Dates come as text in ISO format ("2017-01-01" = January 2017).
    """
    # The API returns 100 rows by default; 5000 is its maximum and covers decades of monthly data.
    params = {"ids": series_id, "limit": 5000, "format": "json"}
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()  # stop with a clear error if the API answered 4xx/5xx
    rows = response.json()["data"]  # e.g. [["2016-12-01", 100.0], ["2017-01-01", 101.5859], ...]

    # Skip months without data (None): a missing month is honest; 0 would break wage / CPI.
    return [(date, value) for date, value in rows if value is not None]


if __name__ == "__main__":
    # Quick manual check: python src/sources.py
    cpi = fetch_series(SERIES["cpi"])
    print(f"CPI: {len(cpi)} months, first {cpi[0]}, last {cpi[-1]}")
