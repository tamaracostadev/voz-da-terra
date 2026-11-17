"""Testes com dados artificiais de desenvolvimento (NÃO são dados do projeto)."""

from __future__ import annotations

import unittest

import pandas as pd

from voz_da_terra.constants import DEC_COLS, decendio_label
from voz_da_terra.metrics import (
    filter_scope, municipality_ranking, municipality_window_matrix,
    period_coverage, soil_period_heatmap,
)


def row(geo, municipio, solo, ciclo, windows):
    record = {
        "geocodigo": geo,
        "municipio": municipio,
        "Cod_Solo": solo,
        "Cod_Ciclo": ciclo,
    }
    record.update({column: 0 for column in DEC_COLS})
    record.update(windows)
    return record


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([
            row("3100001", "Alfa", "11", "20", {"dec28": 20, "dec29": 30}),
            row("3100001", "Alfa", "13", "20", {"dec28": 20, "dec30": 40}),
            row("3100001", "Alfa", "11", "21", {"dec28": 20}),
            row("3100002", "Beta", "11", "20", {"dec29": 20}),
            row("3100003", "Gama", "13", "20", {"dec28": 0}),
        ])

    def test_distinct_municipality_not_rows(self):
        matrix = municipality_window_matrix(self.frame, 20)
        self.assertEqual(int(matrix["dec28"].sum()), 1)
        self.assertEqual(int(matrix["dec29"].sum()), 1)
        self.assertEqual(int(matrix["dec30"].sum()), 0)

    def test_maximum_risk_is_inclusive(self):
        self.assertTrue(municipality_window_matrix(self.frame, 30).loc["3100001", "dec29"])
        self.assertFalse(municipality_window_matrix(self.frame, 30).loc["3100001", "dec30"])
        self.assertTrue(municipality_window_matrix(self.frame, 40).loc["3100001", "dec30"])

    def test_filters_preserve_scope(self):
        selected = filter_scope(self.frame, municipalities=["Alfa"], soil_codes=["11"], cycle_codes=["20"])
        self.assertEqual(len(selected), 1)
        self.assertEqual(int(selected.iloc[0]["dec28"]), 20)

    def test_ranking_and_period_counts(self):
        matrix = municipality_window_matrix(self.frame, 40)
        ranking = municipality_ranking(self.frame, matrix)
        self.assertEqual(ranking.iloc[0]["municipio"], "Alfa")
        self.assertEqual(int(ranking.iloc[0]["decendios_indicados"]), 3)
        periods = period_coverage(matrix)
        self.assertEqual(int(periods.loc[periods["decendio"].eq(28), "municipios"].iloc[0]), 1)

    def test_soil_heatmap_counts_unique_municipalities(self):
        heatmap = soil_period_heatmap(self.frame, 20)
        self.assertEqual(int(heatmap.loc["AD1", "dec28"]), 1)
        self.assertEqual(int(heatmap.loc["AD1", "dec29"]), 1)
        self.assertEqual(int(heatmap.loc["AD3", "dec28"]), 1)

    def test_bad_risk_is_rejected(self):
        with self.assertRaises(ValueError):
            municipality_window_matrix(self.frame, 50)

    def test_label(self):
        self.assertIn("out", decendio_label(28))
        self.assertIn("dez", decendio_label(36))


if __name__ == "__main__":
    unittest.main()
