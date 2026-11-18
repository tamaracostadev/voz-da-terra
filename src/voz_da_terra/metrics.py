"""Métricas independentes da interface, evitando dupla contagem municipal."""

from __future__ import annotations

from pathlib import Path
import unicodedata
from collections.abc import Iterable

import pandas as pd

from .constants import DEC_COLS, RISK_CODES, SOIL_LABELS


def load_processed(path: Path | str) -> pd.DataFrame:
    """Lê a base curada preservando geocódigos e códigos como identificadores."""
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = set(DEC_COLS) - set(frame.columns)
    if missing:
        raise ValueError(f"Decêndios ausentes: {sorted(missing)}")
    for column in DEC_COLS:
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype("int16")
    return frame


def filter_scope(
    frame: pd.DataFrame,
    *,
    municipalities: list[str] | None = None,
    soil_codes: list[str] | None = None,
    cycle_codes: list[str] | None = None,
) -> pd.DataFrame:
    """Aplica apenas os filtros explicitamente escolhidos pelo usuário."""
    selected = frame
    if municipalities:
        selected = selected[selected["municipio"].isin(municipalities)]
    if soil_codes:
        selected = selected[selected["Cod_Solo"].isin(soil_codes)]
    if cycle_codes:
        selected = selected[selected["Cod_Ciclo"].isin(cycle_codes)]
    return selected.copy()


def recommended_decendios(frame: pd.DataFrame) -> list[int]:
    """Períodos que possuem ao menos uma indicação oficial no conjunto lido.

    Código zero não significa ausência de dados: significa que aquele período
    não tem recomendação no recorte. Mantemos as 36 colunas no arquivo curado.
    """
    if frame.empty:
        return []
    recommendations = frame[list(DEC_COLS)].isin(RISK_CODES).any(axis=0)
    return [int(column[3:]) for column, present in recommendations.items() if present]


def search_municipalities(municipalities: Iterable[str], query: str) -> list[str]:
    """Busca municipal por trechos de nome, sem diferença entre acentos/maiúsculas.

    Vários termos separados por vírgula permitem comparar cidades sem precisar
    de um multiselect com centenas de opções em uma tela pequena.
    """
    def normalize(value: str) -> str:
        return "".join(
            char for char in unicodedata.normalize("NFKD", value.casefold())
            if not unicodedata.combining(char)
        )

    terms = [normalize(part.strip()) for part in query.split(",") if part.strip()]
    if not terms:
        return []
    return sorted({
        municipality for municipality in municipalities
        if any(term in normalize(municipality) for term in terms)
    })


def municipality_window_matrix(frame: pd.DataFrame, max_risk: int) -> pd.DataFrame:
    """Matriz booleana município x decêndio.

    True significa que existe AO MENOS UMA combinação de solo e ciclo
    indicada dentro do risco selecionado. Não garante aptidão para toda
    propriedade daquele município.
    """
    if max_risk not in RISK_CODES:
        raise ValueError(f"Risco inválido: {max_risk}")
    if frame.empty:
        return pd.DataFrame(columns=DEC_COLS, dtype=bool)

    candidates = frame.loc[:, DEC_COLS].isin([r for r in RISK_CODES if r <= max_risk])
    candidates.insert(0, "geocodigo", frame["geocodigo"].to_numpy())
    return candidates.groupby("geocodigo", sort=True)[list(DEC_COLS)].any()


def period_coverage(matrix: pd.DataFrame) -> pd.DataFrame:
    """Número de municípios distintos com indicação em cada decêndio."""
    counts = matrix.sum(axis=0).reindex(DEC_COLS, fill_value=0)
    return pd.DataFrame({
        "decendio": list(range(1, 37)),
        "municipios": [int(value) for value in counts],
    })


def municipality_ranking(frame: pd.DataFrame, matrix: pd.DataFrame) -> pd.DataFrame:
    """Quantidade de decêndios indicados por município, sem somar linhas."""
    if matrix.empty:
        return pd.DataFrame(columns=["geocodigo", "municipio", "decendios_indicados"])
    names = frame.drop_duplicates("geocodigo").set_index("geocodigo")["municipio"]
    ranking = matrix.sum(axis=1).astype(int).rename("decendios_indicados").to_frame()
    ranking["municipio"] = ranking.index.map(names)
    return (
        ranking.reset_index()
        .sort_values(["decendios_indicados", "municipio"], ascending=[False, True])
        .reset_index(drop=True)
    )


def soil_period_heatmap(frame: pd.DataFrame, max_risk: int) -> pd.DataFrame:
    """Linhas: classes de solo. Colunas: decêndios. Valores: municípios únicos."""
    rows = {}
    for soil_code, subset in frame.groupby("Cod_Solo", sort=True):
        matrix = municipality_window_matrix(subset, max_risk)
        rows[SOIL_LABELS.get(soil_code, f"Solo {soil_code}")] = (
            matrix.sum(axis=0).reindex(DEC_COLS, fill_value=0).astype(int)
        )
    if not rows:
        return pd.DataFrame(columns=DEC_COLS)
    return pd.DataFrame.from_dict(rows, orient="index").reindex(columns=DEC_COLS)
