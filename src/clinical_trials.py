"""Small ClinicalTrials.gov lookup for explicitly mapped company sponsors."""

from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://clinicaltrials.gov/api/v2/studies"
SEARCH_URL = "https://clinicaltrials.gov/search"
PAGE_SIZE = 1000
DISPLAY_TRIAL_LIMIT = 10

# Keep sponsor matching explicit: a ticker is never treated as a sponsor name.
SPONSOR_ALIASES: dict[str, tuple[str, ...]] = {
    "NTLA": ("Intellia Therapeutics",),
    "VRTX": ("Vertex Pharmaceuticals",),
    "GILD": ("Gilead Sciences", "Kite, A Gilead Company"),
    "AMGN": ("Amgen",),
    "REGN": ("Regeneron Pharmaceuticals",),
}

ACTIVE_STATUSES = {
    "NOT_YET_RECRUITING",
    "RECRUITING",
    "ENROLLING_BY_INVITATION",
    "ACTIVE_NOT_RECRUITING",
}

STATUS_LABELS = {
    "NOT_YET_RECRUITING": "Not yet recruiting",
    "RECRUITING": "Recruiting",
    "ENROLLING_BY_INVITATION": "Enrolling by invitation",
    "ACTIVE_NOT_RECRUITING": "Active, not recruiting",
}

PHASE_LABELS = {
    "EARLY_PHASE1": "Early Phase 1",
    "PHASE1": "Phase 1",
    "PHASE2": "Phase 2",
    "PHASE3": "Phase 3",
    "PHASE4": "Phase 4",
}
DEVELOPMENT_PHASES = {"EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3"}

_COMPANY_SUFFIXES = {"inc", "incorporated", "llc", "ltd", "limited", "corp", "corporation", "company", "co"}


def _normalize_sponsor(name: str) -> str:
    words = re.findall(r"[a-z0-9]+", name.casefold())
    while words and words[-1] in _COMPANY_SUFFIXES:
        words.pop()
    return " ".join(words)


def _study_sponsors(study: dict) -> list[str]:
    sponsor_module = (
        study.get("protocolSection", {})
        .get("sponsorCollaboratorsModule", {})
    )
    names = []
    lead_sponsor = sponsor_module.get("leadSponsor", {}).get("name")
    if lead_sponsor:
        names.append(lead_sponsor)
    names.extend(
        collaborator.get("name", "")
        for collaborator in sponsor_module.get("collaborators", [])
    )
    return names


def _is_company_study(study: dict, aliases: tuple[str, ...]) -> bool:
    alias_names = {_normalize_sponsor(alias) for alias in aliases}
    return any(
        _normalize_sponsor(name) in alias_names
        for name in _study_sponsors(study)
    )


def _matched_sponsor_roles(study: dict, aliases: tuple[str, ...]) -> list[str]:
    alias_names = {_normalize_sponsor(alias) for alias in aliases}
    sponsor_module = (
        study.get("protocolSection", {})
        .get("sponsorCollaboratorsModule", {})
    )
    roles = []
    lead_sponsor = sponsor_module.get("leadSponsor", {}).get("name", "")
    if _normalize_sponsor(lead_sponsor) in alias_names:
        roles.append("Lead sponsor")
    if any(
        _normalize_sponsor(collaborator.get("name", "")) in alias_names
        for collaborator in sponsor_module.get("collaborators", [])
    ):
        roles.append("Collaborator")
    return roles


def _phase_label(phases: list[str]) -> str:
    valid_phases = [
        phase for phase in phases
        if phase and phase.upper() not in {"NA", "N/A", "NOT_APPLICABLE"}
    ]
    if not valid_phases:
        return "Not specified / not applicable"
    return " / ".join(
        PHASE_LABELS.get(phase, phase.replace("_", " ").title())
        for phase in valid_phases
    )


def _pipeline_category(study_type: str, phases: list[str], title: str) -> str:
    """Classify trial activity without treating follow-up or observational records as pipeline trials."""
    normalized_title = title.casefold()
    if re.search(r"long[- ]term follow[- ]?up|\bltfu\b", normalized_title):
        return "Long-term follow-up"
    if study_type == "OBSERVATIONAL":
        return "Observational"
    if "PHASE4" in phases:
        return "Phase 4"
    if study_type == "INTERVENTIONAL" and any(
        phase in DEVELOPMENT_PHASES for phase in phases
    ):
        return "Interventional Phase 1-3"
    return "Other / phase unspecified"


def summarize_studies(
    ticker: str,
    studies: list[dict],
    aliases: tuple[str, ...] | None = None,
) -> dict:
    """Summarize sponsor-matched studies without treating misses as zero data."""
    if aliases is None:
        aliases = SPONSOR_ALIASES.get(ticker.upper(), ())

    if not aliases:
        return {
            "ticker": ticker.upper(),
            "status": "unmapped",
            "sponsor_aliases": [],
            "matched_study_count": None,
            "active_study_count": None,
            "active_lead_sponsored_count": None,
            "active_collaborator_only_count": None,
            "lead_development_trial_count": None,
            "lead_other_active_study_count": None,
            "collaborator_development_trial_count": None,
            "collaborator_other_active_study_count": None,
            "lead_other_activity_categories": {},
            "collaborator_other_activity_categories": {},
            "phase_counts": {},
            "status_counts": {},
            "collaborator_phase_counts": {},
            "collaborator_status_counts": {},
            "active_studies": [],
        }

    matched_studies = [study for study in studies if _is_company_study(study, aliases)]
    active_studies = []
    active_lead_sponsored_count = 0
    active_collaborator_only_count = 0
    lead_development_trial_count = 0
    lead_other_active_study_count = 0
    collaborator_development_trial_count = 0
    collaborator_other_active_study_count = 0
    lead_other_activity_categories: dict[str, int] = {}
    collaborator_other_activity_categories: dict[str, int] = {}
    phase_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    collaborator_phase_counts: dict[str, int] = {}
    collaborator_status_counts: dict[str, int] = {}

    for study in matched_studies:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        status = status_module.get("overallStatus", "UNKNOWN")

        if status not in ACTIVE_STATUSES:
            continue

        phases = design_module.get("phases", [])
        phase = _phase_label(phases)
        study_type = design_module.get("studyType", "NOT SPECIFIED")
        title = identification.get("briefTitle", "Untitled study")
        pipeline_category = _pipeline_category(study_type, phases, title)
        is_development_trial = pipeline_category == "Interventional Phase 1-3"
        status_label = STATUS_LABELS.get(status, status.replace("_", " ").title())
        matched_roles = _matched_sponsor_roles(study, aliases)
        is_lead_sponsored = "Lead sponsor" in matched_roles
        if is_lead_sponsored:
            active_lead_sponsored_count += 1
            if is_development_trial:
                lead_development_trial_count += 1
            else:
                lead_other_active_study_count += 1
                lead_other_activity_categories[pipeline_category] = (
                    lead_other_activity_categories.get(pipeline_category, 0) + 1
                )
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            status_counts[status_label] = status_counts.get(status_label, 0) + 1
        else:
            active_collaborator_only_count += 1
            if is_development_trial:
                collaborator_development_trial_count += 1
            else:
                collaborator_other_active_study_count += 1
                collaborator_other_activity_categories[pipeline_category] = (
                    collaborator_other_activity_categories.get(pipeline_category, 0) + 1
                )
            collaborator_phase_counts[phase] = collaborator_phase_counts.get(phase, 0) + 1
            collaborator_status_counts[status_label] = (
                collaborator_status_counts.get(status_label, 0) + 1
            )
        active_studies.append({
            "nct_id": identification.get("nctId", "N/A"),
            "title": title,
            "status": status_label,
            "phase": phase,
            "study_type": study_type,
            "pipeline_category": pipeline_category,
            "lead_sponsor": sponsor_module.get("leadSponsor", {}).get("name", "N/A"),
            "matched_roles": matched_roles,
        })

    return {
        "ticker": ticker.upper(),
        "status": "ok" if matched_studies else "no_exact_match",
        "sponsor_aliases": list(aliases),
        "matched_study_count": len(matched_studies),
        "active_study_count": len(active_studies),
        "active_lead_sponsored_count": active_lead_sponsored_count,
        "active_collaborator_only_count": active_collaborator_only_count,
        "lead_development_trial_count": lead_development_trial_count,
        "lead_other_active_study_count": lead_other_active_study_count,
        "collaborator_development_trial_count": collaborator_development_trial_count,
        "collaborator_other_active_study_count": collaborator_other_active_study_count,
        "lead_other_activity_categories": lead_other_activity_categories,
        "collaborator_other_activity_categories": collaborator_other_activity_categories,
        "phase_counts": phase_counts,
        "status_counts": status_counts,
        "collaborator_phase_counts": collaborator_phase_counts,
        "collaborator_status_counts": collaborator_status_counts,
        "active_studies": active_studies,
    }


def fetch_clinical_trial_summary(ticker: str, timeout: float = 20.0) -> dict:
    """Fetch sponsor-matched studies from the public ClinicalTrials.gov API v2."""
    ticker = ticker.upper()
    aliases = SPONSOR_ALIASES.get(ticker, ())
    if not aliases:
        return summarize_studies(ticker, [], aliases=())

    found_studies: dict[str, dict] = {}
    try:
        for alias in aliases:
            page_token = None
            seen_page_tokens = set()
            while True:
                params = {
                    "format": "json",
                    "query.spons": alias,
                    "pageSize": PAGE_SIZE,
                    "countTotal": "true",
                }
                if page_token:
                    params["pageToken"] = page_token
                request = Request(
                    f"{API_URL}?{urlencode(params)}",
                    headers={"User-Agent": "AI-Financial-Agent-biotech-research/1.0"},
                )
                with urlopen(request, timeout=timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                for study in payload.get("studies", []):
                    identification = (
                        study.get("protocolSection", {})
                        .get("identificationModule", {})
                    )
                    nct_id = identification.get("nctId")
                    if nct_id and _is_company_study(study, aliases):
                        found_studies[nct_id] = study

                next_page_token = payload.get("nextPageToken")
                if not next_page_token or next_page_token in seen_page_tokens:
                    break
                seen_page_tokens.add(next_page_token)
                page_token = next_page_token
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return {
            "ticker": ticker,
            "status": "error",
            "message": str(error),
            "sponsor_aliases": list(aliases),
            "matched_study_count": None,
            "active_study_count": None,
            "active_lead_sponsored_count": None,
            "active_collaborator_only_count": None,
            "lead_development_trial_count": None,
            "lead_other_active_study_count": None,
            "collaborator_development_trial_count": None,
            "collaborator_other_active_study_count": None,
            "lead_other_activity_categories": {},
            "collaborator_other_activity_categories": {},
            "phase_counts": {},
            "status_counts": {},
            "collaborator_phase_counts": {},
            "collaborator_status_counts": {},
            "active_studies": [],
        }

    summary = summarize_studies(ticker, list(found_studies.values()), aliases=aliases)
    summary["source_url"] = f"{SEARCH_URL}?{urlencode({'term': aliases[0]})}"
    return summary


def display_clinical_trial_summary(summary: dict) -> None:
    """Print a compact, cautious pipeline-data prototype summary."""
    ticker = summary.get("ticker", "N/A")
    print(f"\n=== Clinical trial activity: {ticker} ===")
    print("Source: ClinicalTrials.gov (public registry); activity counts are not efficacy evidence.")

    status = summary.get("status")
    if status == "unmapped":
        print("No sponsor aliases are configured; trial data was not searched.")
        return
    if status == "error":
        print(f"Trial data unavailable: {summary.get('message', 'request failed')}")
        return
    if status == "no_exact_match":
        print(
            "No studies matched the configured sponsor aliases: "
            + ", ".join(summary.get("sponsor_aliases", []))
        )
        return

    print("Configured sponsor aliases: " + "; ".join(summary["sponsor_aliases"]))
    print(f"Alias-matched studies (lead sponsor or collaborator): {summary['matched_study_count']}")
    print(f"Active alias-matched studies: {summary['active_study_count']}")
    print(f"Active company-led studies: {summary['active_lead_sponsored_count']}")
    print(f"Active collaborator-only studies: {summary['active_collaborator_only_count']}")
    print(
        "Company-led interventional development trials (Early Phase 1–Phase 3): "
        f"{summary['lead_development_trial_count']}"
    )
    print(f"Other active company-led studies: {summary['lead_other_active_study_count']}")
    for category, count in sorted(summary["lead_other_activity_categories"].items()):
        print(f"  {category}: {count}")
    print(
        "Collaborator-only interventional development trials (Early Phase 1–Phase 3): "
        f"{summary['collaborator_development_trial_count']}"
    )
    print(
        "Other active collaborator-only studies: "
        f"{summary['collaborator_other_active_study_count']}"
    )
    for category, count in sorted(summary["collaborator_other_activity_categories"].items()):
        print(f"  {category}: {count}")
    print("Active company-led studies by phase:")
    if summary["phase_counts"]:
        for phase, count in sorted(summary["phase_counts"].items()):
            print(f"  {phase}: {count}")
    else:
        print("  None reported")

    print("Active company-led studies by status:")
    if summary["status_counts"]:
        for status_label, count in sorted(summary["status_counts"].items()):
            print(f"  {status_label}: {count}")
    else:
        print("  None")

    print("Active collaborator-only studies by phase:")
    if summary["collaborator_phase_counts"]:
        for phase, count in sorted(summary["collaborator_phase_counts"].items()):
            print(f"  {phase}: {count}")
    else:
        print("  None")

    print("Active collaborator-only studies by status:")
    if summary["collaborator_status_counts"]:
        for status_label, count in sorted(summary["collaborator_status_counts"].items()):
            print(f"  {status_label}: {count}")
    else:
        print("  None")

    development_studies = [
        study
        for study in summary["active_studies"]
        if study["pipeline_category"] == "Interventional Phase 1-3"
        and "Lead sponsor" in study["matched_roles"]
    ]
    print(
        "Active company-led development trial records "
        f"(showing up to {DISPLAY_TRIAL_LIMIT}; registry order):"
    )
    for study in development_studies[:DISPLAY_TRIAL_LIMIT]:
        print(
            f"  {study['nct_id']} | {study['pipeline_category']} | "
            f"{study['phase']} | {study['study_type']} | {study['status']} | "
            f"matched as {', '.join(study['matched_roles'])}; "
            f"lead sponsor: {study['lead_sponsor']} | {study['title']}"
        )
    omitted_count = len(development_studies) - DISPLAY_TRIAL_LIMIT
    if omitted_count > 0:
        print(f"  ... {omitted_count} additional company-led development studies omitted.")
    elif not development_studies:
        print("  None")
    print(f"Study search: {summary.get('source_url', SEARCH_URL)}")
