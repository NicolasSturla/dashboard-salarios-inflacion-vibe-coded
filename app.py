"""Dashboard: did wages beat inflation? Run with:  .\\.venv\\Scripts\\streamlit run app.py"""

import plotly.graph_objects as go
import streamlit as st

from src.calculations import real_wage
from src.database import connect, load_series

# shortcut: Spanish text written here for now; it moves to translations/ in the i18n step.
WAGE_LABELS = {
    "wages_total": "Total",
    "wages_private_registered": "Privado registrado",
    "wages_public": "Público",
    "wages_private_unregistered": "Privado no registrado",
}
DEFAULT_SELECTION = ["wages_total", "wages_private_registered", "wages_public"]


@st.cache_data  # read the database once, not on every click
def load_all() -> dict[str, list[tuple[str, float]]]:
    conn = connect()
    data = {name: load_series(conn, name) for name in ["cpi", *WAGE_LABELS]}
    conn.close()
    return data


data = load_all()
cpi = data["cpi"]

st.set_page_config(page_title="¿Le ganaron los sueldos a la inflación?", layout="wide")
st.title("¿Le ganaron los sueldos a la inflación?")
st.write(
    "Poder de compra del salario en Argentina. **100 = lo que se podía comprar en el mes base.** "
    "Por encima de 100 los sueldos le ganaron a los precios; por debajo, perdieron."
)

# Base month: only months where CPI and every wage series exist, so all lines can start at 100.
common_months = sorted(set.intersection(*(set(dict(data[n])) for n in ["cpi", *WAGE_LABELS])))
col_series, col_base = st.columns([3, 1])
selected = col_series.multiselect(
    "Sectores", options=list(WAGE_LABELS), default=DEFAULT_SELECTION,
    format_func=lambda name: WAGE_LABELS[name],
)
base_date = col_base.selectbox(
    "Mes base", options=common_months, index=common_months.index("2017-01-01"),
    format_func=lambda d: d[:7],
)

if not selected:
    st.info("Elegí al menos un sector.")
    st.stop()

results = {name: real_wage(data[name], cpi, base_date) for name in selected}

# One headline number per sector: purchasing power in the latest month with data.
for column, (name, series) in zip(st.columns(len(results)), results.items()):
    last_date, last_value = series[-1]
    column.metric(
        f"{WAGE_LABELS[name]} ({last_date[:7]})", f"{last_value:.1f}",
        delta=f"{last_value - 100:+.1f}% vs. {base_date[:7]}",
    )

fig = go.Figure()
for name, series in results.items():
    dates, values = zip(*series)
    fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name=WAGE_LABELS[name]))
fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Mes base = 100")
fig.update_layout(yaxis_title="Salario real (base = 100)", hovermode="x unified",
                  legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig, width="stretch")

st.caption(
    f"Fuente: INDEC, vía API Series de Tiempo (datos.gob.ar). IPC hasta {cpi[-1][0][:7]}; "
    "los salarios se publican con unos 2 meses de atraso, por eso las líneas terminan antes. "
    "La serie de privados no registrados es muy volátil y el INDEC la publica con rezago: "
    "interpretarla con cuidado."
)
