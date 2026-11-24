"""Dashboard: did wages beat inflation? Run with:  .\\.venv\\Scripts\\streamlit run app.py"""

import plotly.graph_objects as go
import streamlit as st

from src.calculations import real_wage
from src.database import connect, load_series
from src.i18n import LANGUAGES, t

WAGE_SERIES = ["wages_total", "wages_private_registered", "wages_public", "wages_private_unregistered"]
DEFAULT_SELECTION = WAGE_SERIES[:3]  # unregistered left out until its meaning is verified


@st.cache_data  # read the database once, not on every click
def load_all() -> dict[str, list[tuple[str, float]]]:
    conn = connect()
    data = {name: load_series(conn, name) for name in ["cpi", *WAGE_SERIES]}
    conn.close()
    return data


# Page config must be the first Streamlit call, before the language is known: title in both.
st.set_page_config(page_title="Salarios vs. inflación | Wages vs. inflation", layout="wide")

# ?lang=en in the URL opens the page in English (handy for sharing); anything unknown -> Spanish.
url_lang = st.query_params.get("lang", "es")
lang = st.radio(
    "Idioma / Language", options=list(LANGUAGES), format_func=LANGUAGES.get,
    index=list(LANGUAGES).index(url_lang) if url_lang in LANGUAGES else 0,
    horizontal=True, label_visibility="collapsed",
)

data = load_all()
cpi = data["cpi"]

st.title(t("title", lang))
st.write(t("intro", lang))

# Base month: only months where CPI and every wage series exist, so all lines can start at 100.
common_months = sorted(set.intersection(*(set(dict(data[n])) for n in ["cpi", *WAGE_SERIES])))
col_series, col_base = st.columns([3, 1])
selected = col_series.multiselect(
    t("sectors", lang), options=WAGE_SERIES, default=DEFAULT_SELECTION,
    format_func=lambda name: t(name, lang),
)
base_date = col_base.selectbox(
    t("base_month", lang), options=common_months, index=common_months.index("2017-01-01"),
    format_func=lambda d: d[:7],
)

if not selected:
    st.info(t("pick_a_sector", lang))
    st.stop()

results = {name: real_wage(data[name], cpi, base_date) for name in selected}

# One headline number per sector: purchasing power in the latest month with data.
for column, (name, series) in zip(st.columns(len(results)), results.items()):
    last_date, last_value = series[-1]
    column.metric(
        f"{t(name, lang)} ({last_date[:7]})", f"{last_value:.1f}",
        delta=t("delta", lang, change=last_value - 100, base=base_date[:7]),
    )

fig = go.Figure()
for name, series in results.items():
    dates, values = zip(*series)
    fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name=t(name, lang)))
fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text=t("base_line", lang))
fig.update_layout(yaxis_title=t("y_axis", lang), hovermode="x unified",
                  legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig, width="stretch")

st.caption(t("source", lang, cpi_end=cpi[-1][0][:7]))
