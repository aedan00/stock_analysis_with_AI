import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from main import (  # noqa: E402
    biotech_score,
    biotech_score_breakdown,
    compare_biotech_tickers,
    format_cash_runway,
    format_currency,
    format_percentage,
)
from fundamentals.fundamental_analysis import build_biotech_comparison_metrics  # noqa: E402


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
    def test_currency_formatter_shows_billion_precision_and_keeps_millions_compact(self):
        self.assertEqual(format_currency(3_100_000_000), "$3.10B")
        self.assertEqual(format_currency(3_059_600_000), "$3.06B")
        self.assertEqual(format_currency(40_400_000), "$40.4M")

    def test_breakdown_components_sum_to_total_score(self):
        metrics = make_metrics()
        breakdown = biotech_score_breakdown(metrics)

        self.assertEqual(
            breakdown,
            {
                "liquidity": 20.0,
                "free_cash_flow_margin": 10.0,
                "net_margin": 10.0,
                "revenue_growth": 5.0,
            },
        )
        self.assertEqual(sum(breakdown.values()), biotech_score(metrics))

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
        self.assertIn("Score breakdown (points; N/A means unavailable)", report)
        self.assertIn("Liquidity", report)
        self.assertIn("+20.0", report)
        self.assertIn("N/A", report)

        complete_section, partial_section = report.split("=== Partial data (<4/4) ===")
        self.assertIn("=== Complete data (4/4) ===", complete_section)
        self.assertIn("FULL", complete_section)
        self.assertNotIn("PART", complete_section)
        self.assertIn("PART", partial_section)

    def test_complete_data_does_not_trigger_incomplete_warning(self):
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers({"FULL": make_metrics()})

        self.assertNotIn("Warning: incomplete scores", output.getvalue())

    def test_comparison_displays_average_operating_cash_flow_with_runway(self):
        metrics = make_metrics()
        metrics["cash_position"].update({
            "total_cash": 1_500_000_000,
            "net_cash": 900_000_000,
            "average_operating_cash_flow": -500_000_000,
            "cash_runway_years": 2.0,
            "cash_runway_periods": 3,
        })
        metrics["balance_sheet"]["total_debt"] = 600_000_000
        metrics["statement_periods"] = {
            "balance_sheet_as_of": "2025-12-31",
            "operating_cash_flow_periods": [
                "2025-12-31",
                "2024-12-31",
                "2023-12-31",
            ],
        }
        metrics["research_and_development"] = {
            "expense": 1_200_000_000,
            "intensity": 0.2,
        }
        output = StringIO()

        with redirect_stdout(output):
            compare_biotech_tickers({"TEST": metrics})

        report = output.getvalue()
        self.assertIn("Cash", report)
        self.assertIn("Debt", report)
        self.assertIn("Net Cash", report)
        self.assertIn("Avg OpCF", report)
        self.assertIn("$1.50B", report)
        self.assertIn("$600.0M", report)
        self.assertIn("$900.0M", report)
        self.assertIn("$-500.0M", report)
        self.assertIn("2.0 yrs (3yr avg)", report)
        self.assertIn("Statement periods", report)
        self.assertIn("2025-12-31", report)
        self.assertIn("2024-12-31, 2023-12-31", report)
        self.assertIn("R&D investment context (informational only; not scored)", report)
        self.assertIn("$1.20B", report)
        self.assertIn("20.0%", report)

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


class CashRunwayTests(unittest.TestCase):
    def build_metrics(self, cash, operating_cash_flow, debt=0):
        balance_sheet = pd.DataFrame(
            {"2025-12-31": [cash, debt]},
            index=["Cash And Cash Equivalents At Carrying Value", "Total Debt"],
        )
        operating_cash_flows = (
            operating_cash_flow
            if isinstance(operating_cash_flow, list)
            else [operating_cash_flow]
        )
        cash_flow = pd.DataFrame(
            [operating_cash_flows, [-100] * len(operating_cash_flows)],
            index=["Operating Cash Flow", "Capital Expenditure"],
            columns=[f"{2025 - index}-12-31" for index in range(len(operating_cash_flows))],
        )
        return build_biotech_comparison_metrics(
            "TEST",
            {
                "info": {},
                "income_statement": pd.DataFrame(),
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow,
            },
        )

    def test_negative_operating_cash_flow_produces_runway_estimate(self):
        metrics = self.build_metrics(cash=2_000, operating_cash_flow=-500)

        self.assertEqual(metrics["cash_position"]["cash_runway_years"], 4.0)
        self.assertEqual(metrics["cash_position"]["cash_runway_periods"], 1)
        self.assertEqual(format_cash_runway(4.0, -500, 1), "4.0 yrs (1yr avg)")

    def test_runway_uses_average_of_up_to_three_recent_years(self):
        metrics = self.build_metrics(
            cash=1_200,
            operating_cash_flow=[-300, -600, -900, -12_000],
        )

        self.assertEqual(metrics["cash_position"]["average_operating_cash_flow"], -600)
        self.assertEqual(metrics["cash_position"]["cash_runway_periods"], 3)
        self.assertEqual(metrics["cash_position"]["cash_runway_years"], 2.0)
        self.assertEqual(
            metrics["statement_periods"]["operating_cash_flow_periods"],
            ["2025-12-31", "2024-12-31", "2023-12-31"],
        )
        self.assertEqual(
            metrics["statement_periods"]["balance_sheet_as_of"],
            "2025-12-31",
        )

    def test_rd_intensity_is_rd_expense_divided_by_revenue(self):
        income_statement = pd.DataFrame(
            {"2025-12-31": [2_000, 500]},
            index=["Total Revenue", "Research And Development"],
        )
        metrics = build_biotech_comparison_metrics(
            "TEST",
            {
                "info": {},
                "income_statement": income_statement,
                "balance_sheet": pd.DataFrame({"2025-12-31": [2_000, 0]}, index=[
                    "Cash And Cash Equivalents At Carrying Value", "Total Debt",
                ]),
                "cash_flow": pd.DataFrame({"2025-12-31": [-100, -50]}, index=[
                    "Operating Cash Flow", "Capital Expenditure",
                ]),
            },
        )

        rd_metrics = metrics["research_and_development"]
        score_with_rd_data = biotech_score(metrics)
        metrics.pop("research_and_development")

        self.assertEqual(rd_metrics["expense"], 500)
        self.assertEqual(rd_metrics["intensity"], 0.25)
        self.assertEqual(score_with_rd_data, biotech_score(metrics))

    def test_rd_intensity_is_unavailable_when_revenue_or_rd_is_missing(self):
        for income_statement in (
            pd.DataFrame({"2025-12-31": [None, 500]}, index=[
                "Total Revenue", "Research And Development",
            ]),
            pd.DataFrame({"2025-12-31": [2_000]}, index=["Total Revenue"]),
        ):
            metrics = build_biotech_comparison_metrics(
                "TEST",
                {
                    "info": {},
                    "income_statement": income_statement,
                    "balance_sheet": pd.DataFrame(),
                    "cash_flow": pd.DataFrame(),
                },
            )
            self.assertIsNone(metrics["research_and_development"]["intensity"])

    def test_missing_periods_are_ignored_in_average(self):
        metrics = self.build_metrics(
            cash=2_250,
            operating_cash_flow=[None, -500, -1_000],
        )

        self.assertEqual(metrics["cash_position"]["average_operating_cash_flow"], -750)
        self.assertEqual(metrics["cash_position"]["cash_runway_periods"], 2)
        self.assertEqual(metrics["cash_position"]["cash_runway_years"], 3.0)

    def test_zero_cash_is_preserved_as_zero_years(self):
        metrics = self.build_metrics(cash=0, operating_cash_flow=-500)

        self.assertEqual(metrics["cash_position"]["total_cash"], 0)
        self.assertEqual(metrics["cash_position"]["cash_runway_years"], 0.0)

    def test_net_cash_is_cash_less_total_debt(self):
        metrics = self.build_metrics(cash=2_000, operating_cash_flow=-500, debt=500)

        self.assertEqual(metrics["cash_position"]["net_cash"], 1_500)

    def test_net_cash_can_be_negative(self):
        metrics = self.build_metrics(cash=500, operating_cash_flow=-500, debt=2_000)

        self.assertEqual(metrics["cash_position"]["net_cash"], -1_500)

    def test_net_cash_is_unavailable_if_cash_or_debt_is_missing(self):
        missing_cash = self.build_metrics(cash=None, operating_cash_flow=-500, debt=500)
        missing_debt = self.build_metrics(cash=2_000, operating_cash_flow=-500, debt=None)

        self.assertIsNone(missing_cash["cash_position"]["net_cash"])
        self.assertIsNone(missing_debt["cash_position"]["net_cash"])

    def test_positive_operating_cash_flow_has_no_runway_estimate(self):
        metrics = self.build_metrics(cash=2_000, operating_cash_flow=500)

        self.assertIsNone(metrics["cash_position"]["cash_runway_years"])
        self.assertEqual(format_cash_runway(None, 500, 1), "No burn (1yr avg)")

    def test_mixed_periods_with_nonnegative_average_display_no_burn(self):
        metrics = self.build_metrics(cash=2_000, operating_cash_flow=[500, -500])

        self.assertEqual(metrics["cash_position"]["average_operating_cash_flow"], 0)
        self.assertIsNone(metrics["cash_position"]["cash_runway_years"])
        self.assertEqual(format_cash_runway(None, 0, 2), "No burn (2yr avg)")

    def test_missing_operating_cash_flow_has_unavailable_runway(self):
        metrics = self.build_metrics(cash=2_000, operating_cash_flow=None)

        self.assertIsNone(metrics["cash_position"]["cash_runway_years"])
        self.assertEqual(format_cash_runway(None, None, 0), "N/A")

    def test_cash_runway_does_not_change_biotech_score(self):
        metrics = make_metrics()
        original_score = biotech_score(metrics)
        metrics["cash_position"].update({
            "total_cash": 2_000.0,
            "net_cash": 1_500.0,
            "cash_runway_years": 4.0,
            "average_operating_cash_flow": -500.0,
            "cash_runway_periods": 3,
        })
        metrics["balance_sheet"]["total_debt"] = 500.0

        self.assertEqual(biotech_score(metrics), original_score)


if __name__ == "__main__":
    unittest.main()
