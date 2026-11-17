"""Análise exploratória, hipótese pareada e gráficos acadêmicos (Matplotlib)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # execução em CI e ambientes sem interface gráfica
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .constants import DEC_COLS, RISK_CODES, SOIL_LABELS
from .metrics import (
    load_processed, municipality_ranking, municipality_window_matrix,
    period_coverage, recommended_decendios, soil_period_heatmap,
)


def paired_soil_hypothesis(
    data: pd.DataFrame,
    *,
    group: str = "20",
    first_soil: str = "11",
    second_soil: str = "13",
    max_risk: int = 20,
    permutations: int = 2_000,
    seed: int = 2026,
) -> dict:
    """Testa diferença de decêndios recomendados nos MESMOS municípios.

    H0: média das diferenças pareadas (solo B - solo A) igual a zero,
    sob hipótese de sinais intercambiáveis no teste de permutação.
    Não inferir causalidade: classificação do solo e zoneamento são regras
    oficiais e os municípios não formam uma amostra aleatória.
    """
    subset = data[data["Cod_Ciclo"].eq(group)]
    a = municipality_window_matrix(subset[subset["Cod_Solo"].eq(first_soil)], max_risk)
    b = municipality_window_matrix(subset[subset["Cod_Solo"].eq(second_soil)], max_risk)
    common = a.index.intersection(b.index)
    if len(common) < 2:
        return {"status": "inconclusivo", "motivo": "Menos de dois municípios comparáveis"}

    differences = (
        b.loc[common].sum(axis=1).to_numpy(dtype=float)
        - a.loc[common].sum(axis=1).to_numpy(dtype=float)
    )
    observed = float(differences.mean())
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(permutations, len(common)))
    permuted = (signs * differences).mean(axis=1)
    p_value = float((1 + np.count_nonzero(np.abs(permuted) >= abs(observed))) / (permutations + 1))
    return {
        "status": "avaliado",
        "hipotese_nula": "Média das diferenças pareadas no número de decêndios indicados igual a zero",
        "grupo_cultivar": group,
        "solo_a": first_soil,
        "solo_b": second_soil,
        "risco_maximo": max_risk,
        "municipios_pareados": len(common),
        "media_diferenca_b_menos_a": round(observed, 3),
        "mediana_diferenca": float(np.median(differences)),
        "permutacoes": permutations,
        "p_valor_exploratorio_bicaudal": round(p_value, 4),
        "limites": (
            "Resultado exploratório, não causal. A base não é amostra aleatória; "
            "um p-valor não mede a eficácia do plantio nem a chance de perda."
        ),
    }


def generate_analysis(data_path: Path, reports_dir: Path) -> dict:
    data = load_processed(data_path)
    if data.empty:
        raise ValueError("Base curada está vazia")

    figures = reports_dir / "figuras"
    figures.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.titleweight": "bold",
    })

    # 1) Série de posição no calendário (não é série meteorológica ou previsão).
    fig, ax = plt.subplots(figsize=(11, 4.8), constrained_layout=True)
    colors = {20: "#137B62", 30: "#B26E17", 40: "#4361AA"}
    coverage_by_threshold = {}
    active_periods = recommended_decendios(data)
    for threshold in RISK_CODES:
        matrix = municipality_window_matrix(data, threshold)
        period = period_coverage(matrix)
        coverage_by_threshold[threshold] = period
        visible_period = period[period["decendio"].isin(active_periods)]
        ax.plot(
            visible_period["decendio"], visible_period["municipios"],
            color=colors[threshold], marker="o", markersize=3.2,
            linewidth=2, label=f"Risco até {threshold}%",
        )
    # Focar os períodos com indicação evita 27 pontos sem informação útil.
    # As demais datas continuam no CSV e não são apagadas da auditoria.
    if active_periods:
        ax.set_xticks(active_periods)
        ax.set_xlim(min(active_periods) - 0.25, max(active_periods) + 0.25)
    ax.set_xlabel("Decêndio (outubro a dezembro, neste recorte)")
    ax.set_ylabel("Municípios com ao menos uma indicação")
    ax.set_title("Feijão de sequeiro em MG — municípios por janela de plantio")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(loc="upper left", frameon=False)
    fig.savefig(figures / "01_municipios_por_decendio.png", dpi=170)
    plt.close(fig)

    # 2) Cobertura municipal dentro de três limites de risco.
    coverages = {
        threshold: int(municipality_window_matrix(data, threshold).any(axis=1).sum())
        for threshold in RISK_CODES
    }
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    x = np.arange(3)
    bars = ax.bar(x, list(coverages.values()), color=[colors[r] for r in RISK_CODES], width=0.55)
    ax.set_xticks(x, [f"Até {risk}%" for risk in RISK_CODES])
    ax.set_ylim(0, int(data["geocodigo"].nunique() * 1.12))
    ax.set_ylabel("Municípios com ao menos um decêndio indicado")
    ax.set_title("Cobertura municipal por nível máximo de risco")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                f"{int(bar.get_height())}", ha="center", fontweight="bold")
    fig.savefig(figures / "02_cobertura_risco.png", dpi=170)
    plt.close(fig)

    # 3) Distribuição solo x período para o nível mais conservador.
    heatmap = soil_period_heatmap(data, 20)
    active_cols = [col for col in DEC_COLS if heatmap[col].sum() > 0]
    if active_cols:
        image = heatmap[active_cols]
        fig, ax = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
        artist = ax.imshow(image.to_numpy(dtype=int), cmap="YlGnBu", aspect="auto")
        ax.set_xticks(range(len(active_cols)), [str(int(c[3:])) for c in active_cols])
        ax.set_yticks(range(len(image.index)), image.index)
        ax.set_xlabel("Decêndio")
        ax.set_ylabel("Classe de água disponível no solo")
        ax.set_title("Municípios com recomendação de risco até 20%, por solo")
        fig.colorbar(artist, ax=ax, label="Municípios distintos")
        fig.savefig(figures / "03_calor_solo_decendio.png", dpi=170)
        plt.close(fig)

    peak = coverage_by_threshold[40].sort_values(
        ["municipios", "decendio"], ascending=[False, True]
    ).iloc[0]
    ranking = municipality_ranking(data, municipality_window_matrix(data, 20))
    result = {
        "recorte": "Feijão, Minas Gerais, manejo sequeiro, safra 2026/2027",
        "registros": len(data),
        "municipios_distintos": int(data["geocodigo"].nunique()),
        "classes_solo": sorted(SOIL_LABELS.get(v, v) for v in data["Cod_Solo"].unique()),
        "grupos_cultivar": sorted(data["Cod_Ciclo"].unique()),
        "municipios_com_indicacao_por_risco_maximo": {str(k): v for k, v in coverages.items()},
        "pico_decendio_risco_ate_40": {
            "decendio": int(peak["decendio"]),
            "municipios": int(peak["municipios"]),
        },
        "municipios_com_mais_janelas_ate_20": ranking.head(10).to_dict(orient="records"),
        "hipotese_solo_pareada": paired_soil_hypothesis(data),
        "avisos": [
            "A união por município não substitui informações de solo e ciclo da propriedade.",
            "Os números são janelas oficiais do ZARC, não previsões do tempo.",
            "Não há estimativa observada de perdas evitadas ou agricultores atendidos.",
        ],
    }
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "analise.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/processed/zarc_feijao_mg_sequeiro.csv.gz"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    print(json.dumps(generate_analysis(args.data, args.reports_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
