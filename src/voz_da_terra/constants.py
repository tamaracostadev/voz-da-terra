"""Contratos de dados e recorte validado para o MVP acadêmico."""

from __future__ import annotations

DEC_COLS = tuple(f"dec{i}" for i in range(1, 37))
RISK_CODES = (20, 30, 40)

TARGET_CROP = "Feijão"
TARGET_UF = "MG"
TARGET_MANAGEMENT = "Sequeiro"

SOURCE_URL = (
    "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-"
    "dc8ff323b96f/resource/139e5a60-1f43-4cc8-aeab-a35dbbf816c0/"
    "download/dados-abertos-tabua-de-risco-safra-2026-2027.csv"
)
DICTIONARY_URL = (
    "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-"
    "dc8ff323b96f/resource/bebb0ebb-bc75-460c-b900-a7a1ebd87bee/"
    "download/dicionario-de-dados-tabua-de-risco-2026.pdf"
)

SOIL_LABELS = {
    "11": "AD1",
    "12": "AD2",
    "13": "AD3",
    "14": "AD4",
    "15": "AD5",
    "16": "AD6",
}

# Instrução Normativa SPA/MAPA nº 1/2022 (com alteração de 05/08/2022).
# AD = água disponível no solo; o valor é expresso em mm de água/cm de solo.
SOIL_AD_RANGES = {
    "11": "0,34 a <0,46 mm/cm",
    "12": "0,46 a <0,61 mm/cm",
    "13": "0,61 a <0,80 mm/cm",
    "14": "0,80 a <1,06 mm/cm",
    "15": "1,06 a <1,40 mm/cm",
    "16": "≥1,40 mm/cm",
}
SOIL_CLASSIFICATION_URL = (
    "https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/"
    "programa-nacional-de-zoneamento-agricola-de-risco-climatico/"
    "classificacao-de-solo"
)
CYCLE_LABELS = {"20": "Grupo I", "21": "Grupo II", "22": "Grupo III"}

MONTH_LABELS = (
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
)


def decendio_label(number: int) -> str:
    """Legenda de decêndio sem inventar ano de plantio."""
    if not 1 <= number <= 36:
        raise ValueError("O decêndio deve estar entre 1 e 36.")
    month, ten_day_window = divmod(number - 1, 3)
    starts = ("01–10", "11–20", "21–fim")
    return f"{number:02d} ({starts[ten_day_window]}/{MONTH_LABELS[month]})"
