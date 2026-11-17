"""ETL ZARC completo → subconjunto reproduzível do MVP (Feijão/MG/Sequeiro)."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from .constants import (
    DEC_COLS, DICTIONARY_URL, SOURCE_URL, TARGET_CROP,
    TARGET_MANAGEMENT, TARGET_UF,
)
from .metrics import municipality_window_matrix, period_coverage


IDENTIFIERS = [
    "Nome_cultura", "SafraIni", "SafraFin", "Cod_Cultura",
    "Cod_Ciclo", "Cod_Solo", "geocodigo", "UF", "municipio",
    "Cod_Outros_Manejos", "Nome_Outros_Manejos", "Portaria",
]
REQUIRED = set(IDENTIFIERS + list(DEC_COLS))
RISK_TEXT = {"20", "30", "40"}


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_dataset(source: Path, output_dir: Path, reports_dir: Path) -> dict:
    """Lê por blocos; nunca tenta carregar os 249 MB integralmente em memória."""
    if not source.is_file():
        raise FileNotFoundError(f"CSV oficial não encontrado: {source}")
    first_line = pd.read_csv(source, sep=";", encoding="utf-8-sig", nrows=0)
    missing = REQUIRED - set(first_line.columns)
    if missing:
        raise ValueError(f"Colunas do ZARC ausentes: {sorted(missing)}")

    file_sha = checksum(source)
    all_cultures: set[str] = set()
    all_ufs: set[str] = set()
    valid_municipalities: set[str] = set()
    all_geocodes: set[str] = set()
    state_municipalities: dict[str, set[str]] = defaultdict(set)
    pairs_with_recommendation: set[tuple[str, str, str]] = set()
    year_pairs: Counter = Counter()
    scope_parts: list[pd.DataFrame] = []
    total_rows = invalid_location_rows = unknown_dec_code_cells = 0

    for chunk in pd.read_csv(
        source, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False,
        usecols=IDENTIFIERS + list(DEC_COLS), chunksize=50_000,
        on_bad_lines="error",
    ):
        total_rows += len(chunk)
        year_pairs.update(zip(chunk["SafraIni"], chunk["SafraFin"]))
        all_cultures.update(chunk["Nome_cultura"].unique())
        all_ufs.update(chunk["UF"].unique())
        all_geocodes.update(chunk["geocodigo"].unique())

        valid_geo = chunk["geocodigo"].str.fullmatch(r"\d{7}")
        named = chunk["municipio"].str.strip().ne("")
        valid = valid_geo & named
        invalid_location_rows += int((~valid).sum())

        for uf, geo in chunk.loc[valid, ["UF", "geocodigo"]].drop_duplicates().itertuples(index=False, name=None):
            state_municipalities[uf].add(geo)
            valid_municipalities.add(geo)

        period_values = chunk[list(DEC_COLS)]
        unknown_dec_code_cells += int(
            (~period_values.isin({"0", "", *RISK_TEXT})).sum().sum()
        )
        recommended = period_values.isin(RISK_TEXT).any(axis=1)
        for culture, uf, geo in chunk.loc[
            valid & recommended, ["Nome_cultura", "UF", "geocodigo"]
        ].drop_duplicates().itertuples(index=False, name=None):
            pairs_with_recommendation.add((culture, uf, geo))

        in_scope = (
            valid
            & chunk["Nome_cultura"].eq(TARGET_CROP)
            & chunk["UF"].eq(TARGET_UF)
            & chunk["Nome_Outros_Manejos"].eq(TARGET_MANAGEMENT)
        )
        if in_scope.any():
            scope_parts.append(chunk.loc[in_scope, IDENTIFIERS + list(DEC_COLS)].copy())

    if unknown_dec_code_cells:
        raise ValueError(f"Foram encontrados {unknown_dec_code_cells} valores de decêndio não documentados.")
    if len(year_pairs) != 1 or ("2026", "2027") not in year_pairs:
        raise ValueError(f"Safra inesperada: {dict(year_pairs)}")
    if not scope_parts:
        raise ValueError(f"Sem registros para {TARGET_CROP}/{TARGET_UF}/{TARGET_MANAGEMENT}")

    selected = pd.concat(scope_parts, ignore_index=True)
    for decendio in DEC_COLS:
        selected[decendio] = pd.to_numeric(selected[decendio], errors="raise").astype("int16")
    selected.sort_values(["municipio", "geocodigo", "Cod_Solo", "Cod_Ciclo"], inplace=True)
    selected.reset_index(drop=True, inplace=True)

    groups = defaultdict(set)
    for crop, uf, geo in pairs_with_recommendation:
        groups[(crop, uf)].add(geo)
    coverage = pd.DataFrame([
        {
            "cultura": crop,
            "uf": uf,
            "municipios_com_recomendacao": len(municipalities),
            "municipios_da_uf_na_base": len(state_municipalities[uf]),
            "pct_municipios_da_uf_na_base": round(
                100 * len(municipalities) / len(state_municipalities[uf]), 2
            ),
        }
        for (crop, uf), municipalities in groups.items()
    ]).sort_values(["municipios_com_recomendacao", "cultura", "uf"], ascending=[False, True, True])

    matrix_40 = municipality_window_matrix(selected, 40)
    periods_40 = period_coverage(matrix_40)
    risk_municipalities = {
        str(risk): int(municipality_window_matrix(selected, risk).any(axis=1).sum())
        for risk in (20, 30, 40)
    }
    summary = {
        "source_url": SOURCE_URL,
        "dictionary_url": DICTIONARY_URL,
        "source_sha256": file_sha,
        "source_bytes": source.stat().st_size,
        "source_safra": "2026/2027",
        "source_rows": total_rows,
        "source_cultures": len(all_cultures),
        "source_ufs": len(all_ufs),
        "source_distinct_geocodes_including_incomplete": len(all_geocodes),
        "source_distinct_named_municipalities": len(valid_municipalities),
        "rows_with_missing_municipal_label_or_invalid_geocode": invalid_location_rows,
        "unexpected_dec_code_cells": unknown_dec_code_cells,
        "scope": {
            "cultura": TARGET_CROP,
            "uf": TARGET_UF,
            "manejo": TARGET_MANAGEMENT,
            "rows": len(selected),
            "municipalities": int(selected["geocodigo"].nunique()),
            "soil_codes": sorted(selected["Cod_Solo"].unique()),
            "cycle_codes": sorted(selected["Cod_Ciclo"].unique()),
            "portarias": sorted(selected["Portaria"].unique()),
            "decendios_with_recommendation": periods_40.loc[
                periods_40["municipios"].gt(0), "decendio"
            ].tolist(),
            "municipalities_by_max_risk": risk_municipalities,
        },
        "interpretation": (
            "O município entra na contagem se existir pelo menos uma combinação "
            "de solo e ciclo com indicação no decêndio. Isso não equivale a "
            "recomendação para todas as propriedades do município."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    # A base curada completa do MVP cabe em ~52 KB comprimidos e pode ficar no Git.
    # O CSV original de ~249 MB jamais precisa ser versionado.
    selected.to_csv(
        output_dir / "zarc_feijao_mg_sequeiro.csv.gz",
        index=False,
        encoding="utf-8",
        compression={"method": "gzip", "compresslevel": 9, "mtime": 1},
    )
    coverage.to_csv(output_dir / "cobertura_cultura_uf.csv", index=False, encoding="utf-8")
    (reports_dir / "auditoria.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="CSV bruto oficial; não comitar")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    summary = build_dataset(args.source, args.output_dir, args.reports_dir)
    print(json.dumps(summary["scope"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
