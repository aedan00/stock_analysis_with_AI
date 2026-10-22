import json
import sys
import unittest
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from clinical_trials import (  # noqa: E402
    SPONSOR_ALIASES,
    display_clinical_trial_summary,
    fetch_clinical_trial_summary,
    summarize_studies,
)


def make_study(
    nct_id,
    sponsor="Intellia Therapeutics",
    status="RECRUITING",
    phases=None,
    study_type="INTERVENTIONAL",
    collaborators=None,
    title=None,
):
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": title or f"Study {nct_id}",
            },
            "statusModule": {"overallStatus": status},
            "designModule": {"phases": phases or [], "studyType": study_type},
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": sponsor},
                "collaborators": [
                    {"name": name} for name in (collaborators or [])
                ],
            },
        }
    }


class ClinicalTrialSummaryTests(unittest.TestCase):
    def test_summary_keeps_exact_sponsor_matches_and_counts_active_status_and_phase(self):
        studies = [
            make_study("NCT00000001", phases=["PHASE3"]),
            make_study(
                "NCT00000002",
                sponsor="Massachusetts General Hospital",
                collaborators=["Intellia Therapeutics, Inc."],
                status="ACTIVE_NOT_RECRUITING",
                phases=["PHASE1", "PHASE2"],
            ),
            make_study("NCT00000003", status="COMPLETED", phases=["PHASE2"]),
            make_study("NCT00000004", sponsor="Intellia Biotech Research", phases=["PHASE2"]),
        ]

        summary = summarize_studies("NTLA", studies)

        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["matched_study_count"], 3)
        self.assertEqual(summary["active_study_count"], 2)
        self.assertEqual(summary["active_lead_sponsored_count"], 1)
        self.assertEqual(summary["active_collaborator_only_count"], 1)
        self.assertEqual(summary["lead_development_trial_count"], 1)
        self.assertEqual(summary["lead_other_active_study_count"], 0)
        self.assertEqual(summary["collaborator_development_trial_count"], 1)
        self.assertEqual(summary["collaborator_other_active_study_count"], 0)
        self.assertEqual(summary["phase_counts"]["Phase 3"], 1)
        self.assertNotIn("Phase 1 / Phase 2", summary["phase_counts"])
        self.assertEqual(summary["collaborator_phase_counts"]["Phase 1 / Phase 2"], 1)
        self.assertEqual(summary["status_counts"]["Recruiting"], 1)
        self.assertNotIn("Active, not recruiting", summary["status_counts"])
        self.assertEqual(
            summary["collaborator_status_counts"]["Active, not recruiting"],
            1,
        )
        self.assertEqual(
            {study["nct_id"] for study in summary["active_studies"]},
            {"NCT00000001", "NCT00000002"},
        )
        collaborator_trial = next(
            study for study in summary["active_studies"]
            if study["nct_id"] == "NCT00000002"
        )
        self.assertEqual(collaborator_trial["matched_roles"], ["Collaborator"])

    def test_display_labels_led_and_collaborator_counts_separately(self):
        summary = summarize_studies(
            "NTLA",
            [
                make_study("NCT00000011", phases=["PHASE3"]),
                make_study(
                    "NCT00000012",
                    sponsor="Regeneron Pharmaceuticals",
                    collaborators=["Intellia Therapeutics"],
                    phases=["PHASE2"],
                ),
            ],
        )
        output = StringIO()

        with redirect_stdout(output):
            display_clinical_trial_summary(summary)

        report = output.getvalue()
        self.assertIn("Active company-led studies: 1", report)
        self.assertIn("Active collaborator-only studies: 1", report)
        self.assertIn("Active company-led studies by phase", report)
        self.assertIn("Active collaborator-only studies by phase", report)
        self.assertIn("Company-led interventional development trials", report)
        self.assertIn("Other active company-led studies", report)

    def test_display_limits_details_to_lead_sponsored_development_trials(self):
        studies = [
            make_study(f"NCT{index:08d}", phases=["PHASE2"])
            for index in range(40, 53)
        ]
        studies.append(make_study("NCT00000053", phases=["PHASE4"]))
        studies.append(make_study(
            "NCT00000054",
            sponsor="Regeneron Pharmaceuticals",
            collaborators=["Intellia Therapeutics"],
            phases=["PHASE2"],
        ))
        summary = summarize_studies("NTLA", studies)
        output = StringIO()

        with redirect_stdout(output):
            display_clinical_trial_summary(summary)

        report = output.getvalue()
        self.assertIn("Active company-led development trial records (showing up to 10", report)
        self.assertIn("... 3 additional company-led development studies omitted.", report)
        self.assertIn("NCT00000049", report)
        self.assertNotIn("NCT00000050", report)
        self.assertNotIn("NCT00000053", report)
        self.assertNotIn("NCT00000054", report)

    def test_only_interventional_phase_one_to_three_counts_as_development(self):
        studies = [
            make_study("NCT00000021", phases=["EARLY_PHASE1"]),
            make_study("NCT00000022", phases=["PHASE2", "PHASE3"]),
            make_study("NCT00000023", phases=["PHASE4"]),
            make_study("NCT00000024", phases=[], study_type="OBSERVATIONAL"),
            make_study("NCT00000025", phases=[]),
            make_study("NCT00000027", phases=["NA"]),
            make_study(
                "NCT00000026",
                phases=["PHASE3"],
                title="Long-Term Follow-Up Study",
            ),
        ]

        summary = summarize_studies("NTLA", studies)

        self.assertEqual(summary["active_lead_sponsored_count"], 7)
        self.assertEqual(summary["lead_development_trial_count"], 2)
        self.assertEqual(summary["lead_other_active_study_count"], 5)
        self.assertEqual(
            summary["lead_other_activity_categories"],
            {
                "Long-term follow-up": 1,
                "Observational": 1,
                "Other / phase unspecified": 2,
                "Phase 4": 1,
            },
        )
        na_phase_study = next(
            study for study in summary["active_studies"]
            if study["nct_id"] == "NCT00000027"
        )
        self.assertEqual(na_phase_study["phase"], "Not specified / not applicable")
        self.assertEqual(
            {study["pipeline_category"] for study in summary["active_studies"]},
            {
                "Interventional Phase 1-3",
                "Long-term follow-up",
                "Observational",
                "Phase 4",
                "Other / phase unspecified",
            },
        )

    def test_no_exact_sponsor_match_is_not_reported_as_zero_trials(self):
        summary = summarize_studies(
            "NTLA",
            [make_study("NCT00000005", sponsor="Unrelated Therapeutics")],
        )

        self.assertEqual(summary["status"], "no_exact_match")
        self.assertEqual(summary["matched_study_count"], 0)
        self.assertEqual(summary["active_study_count"], 0)

    def test_unmapped_ticker_is_distinguished_from_no_trials(self):
        summary = summarize_studies("UNKNOWN", [])

        self.assertEqual(summary["status"], "unmapped")
        self.assertIsNone(summary["matched_study_count"])
        self.assertIsNone(summary["active_study_count"])

    def test_fetch_builds_sponsor_search_and_summarizes_api_response(self):
        payload = {
            "studies": [make_study("NCT00000006", phases=["PHASE2"])],
            "totalCount": 1,
        }
        response = BytesIO(json.dumps(payload).encode("utf-8"))

        with patch("clinical_trials.urlopen", return_value=response) as mock_urlopen:
            summary = fetch_clinical_trial_summary("NTLA")

        request = mock_urlopen.call_args.args[0]
        query = parse_qs(urlparse(request.full_url).query)
        self.assertEqual(query["query.spons"], ["Intellia Therapeutics"])
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["phase_counts"], {"Phase 2": 1})

    def test_vrtx_alias_matches_registered_vertex_sponsor_name(self):
        self.assertEqual(SPONSOR_ALIASES["VRTX"], ("Vertex Pharmaceuticals",))
        summary = summarize_studies(
            "VRTX",
            [make_study("NCT00000007", sponsor="Vertex Pharmaceuticals Incorporated")],
        )

        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["matched_study_count"], 1)
        self.assertEqual(summary["active_lead_sponsored_count"], 1)

    def test_regn_and_ntla_classify_shared_study_by_sponsor_role(self):
        shared_study = make_study(
            "NCT00000008",
            sponsor="Regeneron Pharmaceuticals, Inc.",
            collaborators=["Intellia Therapeutics, Inc."],
            phases=["PHASE2"],
        )

        regn_summary = summarize_studies("REGN", [shared_study])
        ntla_summary = summarize_studies("NTLA", [shared_study])

        self.assertEqual(SPONSOR_ALIASES["REGN"], ("Regeneron Pharmaceuticals",))
        self.assertEqual(regn_summary["matched_study_count"], 1)
        self.assertEqual(regn_summary["active_lead_sponsored_count"], 1)
        self.assertEqual(regn_summary["active_collaborator_only_count"], 0)
        self.assertEqual(regn_summary["lead_development_trial_count"], 1)
        self.assertEqual(ntla_summary["matched_study_count"], 1)
        self.assertEqual(ntla_summary["active_lead_sponsored_count"], 0)
        self.assertEqual(ntla_summary["active_collaborator_only_count"], 1)
        self.assertEqual(ntla_summary["collaborator_development_trial_count"], 1)

    def test_gild_maps_gilead_and_kite_sponsor_names(self):
        studies = [
            make_study(
                "NCT00000031",
                sponsor="Gilead Sciences, Inc.",
                phases=["PHASE3"],
            ),
            make_study(
                "NCT00000032",
                sponsor="Kite, A Gilead Company",
                phases=["PHASE2"],
            ),
        ]

        summary = summarize_studies("GILD", studies)

        self.assertEqual(
            SPONSOR_ALIASES["GILD"],
            ("Gilead Sciences", "Kite, A Gilead Company"),
        )
        self.assertEqual(summary["matched_study_count"], 2)
        self.assertEqual(summary["active_lead_sponsored_count"], 2)
        self.assertEqual(summary["lead_development_trial_count"], 2)

    def test_amgn_alias_matches_amgen_with_or_without_corporate_suffix(self):
        self.assertEqual(SPONSOR_ALIASES["AMGN"], ("Amgen",))
        studies = [
            make_study("NCT00000041", sponsor="Amgen", phases=["PHASE2"]),
            make_study("NCT00000042", sponsor="Amgen Inc.", phases=["PHASE3"]),
        ]

        summary = summarize_studies("AMGN", studies)

        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["matched_study_count"], 2)
        self.assertEqual(summary["active_lead_sponsored_count"], 2)
        self.assertEqual(summary["lead_development_trial_count"], 2)

    def test_unmapped_ticker_does_not_call_api(self):
        with patch("clinical_trials.urlopen") as mock_urlopen:
            summary = fetch_clinical_trial_summary("UNKNOWN")

        mock_urlopen.assert_not_called()
        self.assertEqual(summary["status"], "unmapped")


if __name__ == "__main__":
    unittest.main()
