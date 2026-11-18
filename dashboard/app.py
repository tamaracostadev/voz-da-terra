"""Painel de BI CitizenTech: janelas oficiais ZARC do Feijão de Sequeiro/MG."""

from __future__ import annotations

import json
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from voz_da_terra.constants import (
    CYCLE_LABELS, DEC_COLS, DICTIONARY_URL,
    SOIL_AD_RANGES, SOIL_CLASSIFICATION_URL, SOIL_LABELS, SOURCE_URL,
)
from voz_da_terra.metrics import (
    filter_scope, load_processed, municipality_ranking, recommended_decendios,
    municipality_window_matrix, period_coverage, search_municipalities,
    soil_period_heatmap,
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
st.markdown("**Consulte as janelas de plantio do feijão de sequeiro em Minas Gerais.**")
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

soil_codes = sorted(data["Cod_Solo"].unique())
cycle_codes = sorted(data["Cod_Ciclo"].unique())
active_decendios = recommended_decendios(data)
if not active_decendios:
    st.error("A base não contém decêndios com indicação do ZARC neste recorte.")
    st.stop()

st.markdown("### Faça sua consulta")
with st.expander("🔎 Buscar e ajustar filtros", expanded=True):
    city_query = st.text_input(
        "1. Município (opcional)",
        placeholder="Ex.: Uberaba ou Uberaba, Uberlândia",
        help="Digite parte do nome. Para comparar vários municípios, separe os nomes por vírgulas. "
        "Deixe vazio para considerar todo o estado.",
    )
    selected_cities = search_municipalities(data["municipio"].unique(), city_query)
    if city_query.strip():
        if selected_cities:
            preview = ", ".join(selected_cities[:4])
            remaining = len(selected_cities) - 4
            extra = f" e mais {remaining}" if remaining > 0 else ""
            st.caption(f"{len(selected_cities)} município(s) encontrado(s): {preview}{extra}.")
            if len(selected_cities) > 10:
                st.caption("Para uma consulta mais específica, digite mais letras do nome.")
        else:
            st.warning("Nenhum município encontrado. Confira a escrita ou limpe o campo.")

    max_risk = st.radio(
        "2. Limite máximo de risco considerado",
        options=[20, 30, 40],
        index=0,
        format_func=lambda value: f"Até {value}%",
        horizontal=True,
        help="Os códigos de risco vêm do ZARC. Selecionar um limite maior não é recomendação para aceitar mais risco.",
    )
    selected_soils = st.pills(
        "3. Água disponível no solo (sem seleção = todas)",
        options=soil_codes,
        selection_mode="multi",
        format_func=lambda code: SOIL_LABELS.get(code, f"Solo {code}"),
        help="Toque nas classes desejadas. AD1 tem menor disponibilidade de água; AD6, maior.",
    )
    selected_cycles = st.pills(
        "4. Grupo de cultivar (sem seleção = todos)",
        options=cycle_codes,
        selection_mode="multi",
        format_func=lambda code: CYCLE_LABELS.get(code, code),
    )
    range_start, range_end = st.slider(
        "5. Período do calendário (decêndios)",
        min_value=min(active_decendios),
        max_value=max(active_decendios),
        value=(min(active_decendios), max(active_decendios)),
        help="Apenas os decêndios com alguma indicação no recorte aparecem neste intervalo.",
    )

with st.expander("Entenda as classes AD1 a AD6"):
    st.markdown(
        "**AD significa água disponível no solo:** quantidade de água que o solo consegue "
        "armazenar e oferecer às plantas. **AD1** representa a menor disponibilidade e "
        "**AD6**, a maior. Não é uma nota de qualidade da terra."
    )
    for code in soil_codes:
        st.caption(f"**{SOIL_LABELS.get(code, code)}:** {SOIL_AD_RANGES.get(code, 'Consultar portaria')}")
    st.markdown(f"[Como identificar a classe do seu solo — MAPA]({SOIL_CLASSIFICATION_URL})")

if city_query.strip() and not selected_cities:
    st.stop()

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

if len(selected_cities) == 1:
    st.markdown(
        f"**Resultado para {selected_cities[0]}:** "
        f"{active_periods} período(s) com alguma indicação até {max_risk}% "
        "nas condições selecionadas."
    )
else:
    st.markdown(
        f"**Resumo:** {municipalities_eligible} de {municipalities_total} municípios "
        f"da consulta têm alguma indicação até {max_risk}% no período escolhido."
    )

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
fig_line.update_layout(height=320, hovermode="x unified", margin=dict(l=10, r=10, t=10, b=10))
fig_line.update_xaxes(dtick=1)
st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
st.caption("Série dos períodos indicados pela portaria; não é histórico meteorológico.")

st.markdown("### 2. Municípios com mais períodos indicados")
ranking_top = ranking[ranking["decendios_indicados"].gt(0)].head(10)
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
    fig_bar.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    fig_bar.update_yaxes(automargin=True)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
st.caption("Ranking por número de períodos, não por produção agrícola.")

st.markdown("### 3. Indicações por classe de solo")
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
        height=380,
        xaxis_title="Decêndio",
        yaxis_title="Água disponível no solo",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
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
