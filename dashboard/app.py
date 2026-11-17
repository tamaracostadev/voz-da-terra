"""Painel de BI CitizenTech: janelas oficiais ZARC do Feijão de Sequeiro/MG."""

from __future__ import annotations

import json
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from voz_da_terra.constants import (
    CYCLE_LABELS, DEC_COLS, DICTIONARY_URL,
    SOIL_LABELS, SOURCE_URL,
)
from voz_da_terra.metrics import (
    filter_scope, load_processed, municipality_ranking,
    municipality_window_matrix, period_coverage, soil_period_heatmap,
)


ROOT = Path(__file__).resolve().parents[1]
CURATED_PATH = ROOT / "data" / "processed" / "zarc_feijao_mg_sequeiro.csv.gz"
AUDIT_PATH = ROOT / "reports" / "auditoria.json"

st.set_page_config(page_title="Voz da Terra | ZARC", page_icon="🌱", layout="wide")


@st.cache_data(show_spinner="Carregando janelas oficiais de plantio...")
def read_data(path: str):
    return load_processed(path)


@st.cache_data(show_spinner=False)
def read_audit(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


st.title("🌱 Voz da Terra")
st.subheader("Janelas de plantio do feijão de sequeiro em Minas Gerais")
st.caption("Safra 2026/2027 | Dados públicos do MAPA | Unidade territorial: município")

if not CURATED_PATH.exists() or not AUDIT_PATH.exists():
    st.error(
        "Arquivos processados indisponíveis. Execute o ETL conforme o README "
        "para gerar a base curada e os metadados da auditoria."
    )
    st.stop()

data = read_data(str(CURATED_PATH))
audit = read_audit(str(AUDIT_PATH))

st.info(
    "**Importante:** este painel interpreta as janelas oficiais do ZARC; "
    "não é previsão do tempo nem garantia de safra. "
    "A indicação depende também do solo e do grupo de cultivar da propriedade."
)

st.sidebar.header("Filtros da análise")
max_risk = st.sidebar.select_slider(
    "Risco climático máximo considerado",
    options=[20, 30, 40],
    value=20,
    format_func=lambda value: f"Até {value}%",
)
soil_codes = sorted(data["Cod_Solo"].unique())
selected_soils = st.sidebar.multiselect(
    "Classes de solo (vazio = todas)",
    options=soil_codes,
    format_func=lambda code: SOIL_LABELS.get(code, f"Solo {code}"),
)
cycle_codes = sorted(data["Cod_Ciclo"].unique())
selected_cycles = st.sidebar.multiselect(
    "Grupos de cultivar (vazio = todos)",
    options=cycle_codes,
    format_func=lambda code: CYCLE_LABELS.get(code, code),
)
selected_cities = st.sidebar.multiselect(
    "Municípios (vazio = todos)",
    options=sorted(data["municipio"].unique()),
)
range_start, range_end = st.sidebar.slider(
    "Intervalo de decêndios",
    min_value=1,
    max_value=36,
    value=(28, 36),
)

filtered = filter_scope(
    data,
    municipalities=selected_cities,
    soil_codes=selected_soils,
    cycle_codes=selected_cycles,
)
if filtered.empty:
    st.warning("Nenhum registro corresponde aos filtros escolhidos.")
    st.stop()

visible_cols = [f"dec{i}" for i in range(range_start, range_end + 1)]
matrix = municipality_window_matrix(filtered, max_risk)
visible = matrix[visible_cols]
periods = period_coverage(matrix)
periods = periods[periods["decendio"].between(range_start, range_end)]
ranking = municipality_ranking(filtered, visible)
heatmap = soil_period_heatmap(filtered, max_risk)[visible_cols]

municipalities_total = int(filtered["geocodigo"].nunique())
municipalities_eligible = int(visible.any(axis=1).sum())
active_periods = int(periods["municipios"].gt(0).sum())

col1, col2, col3 = st.columns(3)
col1.metric("Municípios no filtro", f"{municipalities_total:,}".replace(",", "."))
col2.metric("Com ao menos uma indicação", f"{municipalities_eligible:,}".replace(",", "."))
col3.metric("Decêndios com indicações", f"{active_periods} / {len(visible_cols)}")

st.caption(
    "As contagens mostram municípios com **pelo menos uma** combinação de "
    "solo e ciclo indicada. Não representam área plantada nem número de produtores."
)

st.markdown("### 1. Cobertura ao longo do calendário")
fig_line = px.line(
    periods,
    x="decendio",
    y="municipios",
    markers=True,
    labels={"decendio": "Decêndio", "municipios": "Municípios com indicação"},
    color_discrete_sequence=["#137B62"],
)
fig_line.update_layout(height=340, hovermode="x unified", margin=dict(l=10, r=10, t=10, b=10))
fig_line.update_xaxes(dtick=1)
st.plotly_chart(fig_line, use_container_width=True)
st.caption("Série dos períodos indicados pela portaria; não é histórico meteorológico.")

left, right = st.columns(2, gap="large")
with left:
    st.markdown("### 2. Ranking municipal")
    ranking_top = ranking[ranking["decendios_indicados"].gt(0)].head(15)
    if ranking_top.empty:
        st.warning("Não há municípios com recomendações neste nível de risco e intervalo.")
    else:
        fig_bar = px.bar(
            ranking_top.sort_values("decendios_indicados"),
            x="decendios_indicados",
            y="municipio",
            orientation="h",
            labels={
                "decendios_indicados": "Decêndios com indicação",
                "municipio": "Município",
            },
            color_discrete_sequence=["#4361AA"],
        )
        fig_bar.update_layout(height=480, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("Ranking por número de períodos, não por produção agrícola.")

with right:
    st.markdown("### 3. Disponibilidade por tipo de solo")
    if heatmap.empty:
        st.warning("Sem solos disponíveis nos filtros selecionados.")
    else:
        fig_heat = go.Figure(data=go.Heatmap(
            z=heatmap.to_numpy(dtype=int),
            x=[int(c[3:]) for c in heatmap.columns],
            y=heatmap.index.tolist(),
            colorscale="YlGnBu",
            colorbar=dict(title="Municípios"),
            hovertemplate="Solo %{y}<br>Decêndio %{x}<br>Municípios %{z}<extra></extra>",
        ))
        fig_heat.update_layout(
            height=480,
            xaxis_title="Decêndio",
            yaxis_title="Classe de água disponível no solo",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Cada célula conta municípios únicos para a classe de solo indicada.")

st.markdown("### Três insights a partir dos filtros")
if periods["municipios"].max() > 0:
    peak = periods.sort_values(["municipios", "decendio"], ascending=[False, True]).iloc[0]
    st.markdown(
        f"1. **Pico do calendário:** no decêndio **{int(peak['decendio'])}**, "
        f"**{int(peak['municipios'])} municípios** têm alguma indicação sob os filtros."
    )
else:
    st.markdown("1. **Pico do calendário:** não há indicações neste intervalo e nível de risco.")

coverage_risk_20 = int(municipality_window_matrix(filtered, 20)[visible_cols].any(axis=1).sum())
coverage_risk_40 = int(municipality_window_matrix(filtered, 40)[visible_cols].any(axis=1).sum())
st.markdown(
    f"2. **Sensibilidade ao nível de risco:** {coverage_risk_20} municípios têm "
    f"ao menos um período até 20%, contra {coverage_risk_40} até 40%. "
    "Isso não quantifica perdas reais nem indica que o produtor deva aceitar maior risco."
)

if not heatmap.empty and int(heatmap.to_numpy().sum()) > 0:
    strongest_soil = heatmap.sum(axis=1).sort_values(ascending=False).index[0]
    st.markdown(
        f"3. **Diferença entre solos:** **{strongest_soil}** concentra a maior soma "
        "de indicações município-decêndio neste recorte. É necessário conhecer "
        "o solo da propriedade antes de orientar um plantio."
    )
else:
    st.markdown("3. **Diferença entre solos:** os filtros não retornaram janelas para comparar.")

st.markdown("### Fonte, transparência e limites")
st.markdown(
    f"- [Tábua de risco ZARC 2026/2027 — MAPA]({SOURCE_URL})\n"
    f"- [Dicionário de dados do MAPA]({DICTIONARY_URL})\n"
    f"- **Portaria do recorte:** {', '.join(audit['scope']['portarias'])}\n"
    f"- **SHA-256 do CSV original:** `{audit['source_sha256']}`"
)
st.caption(
    "O painel não coleta dados pessoais. Áudio e WhatsApp são funcionalidades "
    "conceituais do projeto e não estão integrados nesta demonstração."
)

with st.expander("Consultar e baixar os registros filtrados"):
    st.dataframe(
        filtered[["geocodigo", "municipio", "Cod_Solo", "Cod_Ciclo", *DEC_COLS]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Baixar dados filtrados (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="voz_da_terra_filtros.csv",
        mime="text/csv",
    )
