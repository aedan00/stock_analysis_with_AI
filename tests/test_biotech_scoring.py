import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from main import (  # noqa: E402
    biotech_score,
    compare_biotech_tickers,
    format_percentage,
)


def make_metrics(
    current_ratio=2.0,
    free_cash_flow_margin=0.2,
    net_margin=0.1,
    revenue_growth=0.05,
    company="Test Biotech",
):
    return {
        "company": company,
        "market_cap": 1_000_000_000,
        "cash_position": {
            "free_cash_flow": 100_000_000,
            "free_cash_flow_margin": free_cash_flow_margin,
        },
        "balance_sheet": {"current_ratio": current_ratio},
        "profitability": {"net_margin": net_margin},
        "growth": {"revenue_growth": revenue_growth},
    }


class BiotechScoreTests(unittest.TestCase):
    def test_positive_free_cash_flow_margin_scores_above_negative(self):
        positive_score = biotech_score(make_metrics(free_cash_flow_margin=0.2))
        negative_score = biotech_score(make_metrics(free_cash_flow_margin=-0.2))

        self.assertGreater(positive_score, negative_score)

    def test_score_inputs_are_capped_at_configured_bounds(self):
        at_cap = make_metrics(
            current_ratio=3.0,
            free_cash_flow_margin=0.5,
            net_margin=0.5,
            revenue_growth=0.5,
        )
        above_cap = make_metrics(
            current_ratio=10.0,
            free_cash_flow_margin=1.0,
            net_margin=1.0,
            revenue_growth=1.0,
        )

        self.assertEqual(biotech_score(at_cap), biotech_score(above_cap))

    def test_missing_and_non_finite_inputs_are_excluded(self):
        metrics = make_metrics(
            current_ratio=None,
            free_cash_flow_margin=0.1,
            net_margin=float("nan"),
            revenue_growth=0.02,
        )

        self.assertEqual(biotech_score(metrics), 7.0)

    def test_comparison_reports_coverage_and_warns_for_partial_scores(self):
        companies = {
            "FULL": make_metrics(company="Complete Bio"),
            "PART": make_metrics(
                current_ratio=None,
                free_cash_flow_margin=0.1,
                net_margin=float("nan"),
                revenue_growth=0.02,
                company="Partial Bio",
            ),
        }
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers(companies)

        report = output.getvalue()
        self.assertIn("Warning: incomplete scores", report)
        self.assertIn("FULL", report)
        self.assertIn("4/4", report)
        self.assertIn("PART", report)
        self.assertIn("2/4", report)
        self.assertNotIn("nan%", report)

    def test_complete_data_does_not_trigger_incomplete_warning(self):
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers({"FULL": make_metrics()})

        self.assertNotIn("Warning: incomplete scores", output.getvalue())

    def test_empty_comparison_prints_clear_message(self):
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers({})

        self.assertIn("No companies could be ranked", output.getvalue())

    def test_company_with_no_score_metrics_is_skipped(self):
        no_data_metrics = make_metrics(
            current_ratio=None,
            free_cash_flow_margin=None,
            net_margin=None,
            revenue_growth=None,
            company=None,
        )
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers({"SGEN": no_data_metrics})

        report = output.getvalue()
        self.assertIn("Skipping SGEN: no score metrics were available", report)
        self.assertIn("No companies could be ranked", report)
        self.assertNotIn("0/4", report)

    def test_non_finite_percentage_displays_as_unavailable(self):
        self.assertEqual(format_percentage(float("nan")), "N/A")
        self.assertEqual(format_percentage(float("inf")), "N/A")


if __name__ == "__main__":
    unittest.main()
