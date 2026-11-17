"""Testes do ETL com CSV sintético mínimo, nunca confundido com dados do ZARC."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from voz_da_terra.constants import DEC_COLS
from voz_da_terra.metrics import load_processed
from voz_da_terra.pipeline import IDENTIFIERS, build_dataset


class PipelineTest(unittest.TestCase):
    @staticmethod
    def _record(*, geo: str, name: str, state: str = "MG") -> dict[str, str]:
        row = {key: "" for key in IDENTIFIERS + list(DEC_COLS)}
        row.update({
            "Nome_cultura": "Feijão", "SafraIni": "2026", "SafraFin": "2027",
            "Cod_Cultura": "42", "Cod_Ciclo": "20", "Cod_Solo": "11",
            "geocodigo": geo, "UF": state, "municipio": name,
            "Cod_Outros_Manejos": "1", "Nome_Outros_Manejos": "Sequeiro",
            "Portaria": "Portaria-de-teste",
        })
        row.update({col: "0" for col in DEC_COLS})
        row["dec28"] = "20"
        row["dec31"] = "40"
        return row

    def test_builds_compressed_csv_and_excludes_missing_municipalities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw = root / "source.csv"
            with raw.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=IDENTIFIERS + list(DEC_COLS), delimiter=";")
                writer.writeheader()
                writer.writerow(self._record(geo="3100000", name="Cidade Teste"))
                writer.writerow(self._record(geo="4300001", name="", state="RS"))

            output = root / "processed"
            report = build_dataset(raw, output, root / "reports")
            curated = load_processed(output / "zarc_feijao_mg_sequeiro.csv.gz")

            self.assertEqual(2, report["source_rows"])
            self.assertEqual(1, report["rows_with_missing_municipal_label_or_invalid_geocode"])
            self.assertEqual(1, report["scope"]["municipalities"])
            self.assertEqual([28, 31], report["scope"]["decendios_with_recommendation"])
            self.assertEqual(1, len(curated))
            self.assertEqual(20, curated.loc[0, "dec28"])

    def test_rejects_unexpected_risk_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw = root / "source.csv"
            row = self._record(geo="3100000", name="Cidade Teste")
            row["dec28"] = "90"
            with raw.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=IDENTIFIERS + list(DEC_COLS), delimiter=";")
                writer.writeheader()
                writer.writerow(row)

            with self.assertRaisesRegex(ValueError, "não documentados"):
                build_dataset(raw, root / "processed", root / "reports")


if __name__ == "__main__":
    unittest.main()
