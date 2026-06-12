import os
from typing import Any, Dict, List, Optional, Tuple

import yaml


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be an object.")
    return data


def write_create_template(path: str) -> None:
    template = {
        "project_key": "ENG",
        "tickets": [
            {
                "slug": "epic-auth",
                "issue_type": "Epic",
                "summary": "Authentication modernization",
                "epic_name": "Auth Modernization",
                "description": "Upgrade auth flows to support SSO and MFA.",
                "priority": "High",
                "labels": ["security", "auth"],
                "components": ["Authentication"],
                "assignee_username": "Jane Doe",
            },
            {
                "issue_type": "Story",
                "summary": "Implement SAML login",
                "description": "As an enterprise user, I can log in with my IdP.",
                "priority": "High",
                "labels": ["security", "saml"],
                "components": ["Authentication"],
                "story_points": 8,
                "assignee_username": "Jane Doe",
                "parent_epic_slug": "epic-auth",
            },
            {
                "issue_type": "Task",
                "summary": "Add login observability dashboard",
                "description": "Track login success, latency, and failure classes.",
                "priority": "Medium",
                "labels": ["auth", "observability"],
                "components": ["Observability"],
                "story_points": 3,
                "parent_epic_slug": "epic-auth",
            },
        ],
    }
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(template, handle, sort_keys=False)


def validate_local_schema(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if "tickets" not in data or not isinstance(data["tickets"], list) or not data["tickets"]:
        errors.append("'tickets' must be a non-empty list.")
        return errors

    slugs: set = set()
    epic_slugs: set = set()

    for i, ticket in enumerate(data["tickets"], start=1):
        if not isinstance(ticket, dict):
            errors.append(f"tickets[{i}] must be an object.")
            continue

        for required in ["issue_type", "summary"]:
            if required not in ticket or not ticket.get(required):
                errors.append(f"tickets[{i}] missing required field '{required}'.")

        issue_type = str(ticket.get("issue_type", "")).lower()

        if issue_type == "epic":
            slug = ticket.get("slug")
            if not slug:
                errors.append(f"tickets[{i}] Epic must include 'slug'.")
            elif slug in slugs:
                errors.append(f"tickets[{i}] duplicate slug '{slug}'.")
            else:
                slugs.add(slug)
                epic_slugs.add(slug)

        if "story_points" in ticket and not isinstance(ticket["story_points"], (int, float)):
            errors.append(f"tickets[{i}] story_points must be a number.")

        if "labels" in ticket and not isinstance(ticket["labels"], list):
            errors.append(f"tickets[{i}] labels must be a list of strings.")

        components = ticket.get("components")
        if components is not None:
            if not isinstance(components, list) or any(not isinstance(c, str) for c in components):
                errors.append(f"tickets[{i}] components must be a list of strings.")

        if "assignee_account_id" in ticket and not isinstance(ticket["assignee_account_id"], str):
            errors.append(f"tickets[{i}] assignee_account_id must be a string.")

        if "assignee_username" in ticket and not isinstance(ticket["assignee_username"], str):
            errors.append(f"tickets[{i}] assignee_username must be a string.")

        if ticket.get("assignee_account_id") and ticket.get("assignee_username"):
            errors.append(f"tickets[{i}] use only one of assignee_account_id or assignee_username.")

    # Validate parent references after all epics are collected
    for i, ticket in enumerate(data["tickets"], start=1):
        parent = ticket.get("parent_epic_slug")
        if parent and parent not in epic_slugs:
            errors.append(f"tickets[{i}] parent_epic_slug '{parent}' does not match any Epic slug.")

    return errors


def infer_field_ids(name_to_id: Dict[str, str]) -> Dict[str, Optional[str]]:
    story_points_id = os.getenv("JIRA_STORY_POINTS_FIELD_ID")
    epic_name_id = os.getenv("JIRA_EPIC_NAME_FIELD_ID")
    epic_link_id = os.getenv("JIRA_EPIC_LINK_FIELD_ID")
    category_id = os.getenv("JIRA_CATEGORY_FIELD_ID")
    investment_category_id = os.getenv("JIRA_INVESTMENT_CATEGORY_FIELD_ID")
    wsjf_business_value_id = os.getenv("JIRA_WSJF_BUSINESS_VALUE_FIELD_ID")
    wsjf_job_size_id = os.getenv("JIRA_WSJF_JOB_SIZE_FIELD_ID")
    wsjf_risk_opportunity_id = os.getenv("JIRA_WSJF_RISK_OPPORTUNITY_FIELD_ID")
    wsjf_time_criticality_id = os.getenv("JIRA_WSJF_TIME_CRITICALITY_FIELD_ID")
    parent_link_id = os.getenv("JIRA_PARENT_LINK_FIELD_ID")
    funded_by_id = os.getenv("JIRA_FUNDED_BY_FIELD_ID")
    estimated_id = os.getenv("JIRA_ESTIMATED_FIELD_ID")

    if not story_points_id:
        story_points_id = name_to_id.get("Story Points") or name_to_id.get("Story point estimate")
    if not epic_name_id:
        epic_name_id = name_to_id.get("Epic Name")
    if not epic_link_id:
        epic_link_id = name_to_id.get("Epic Link")
    if not category_id:
        category_id = name_to_id.get("Category")
    if not investment_category_id:
        investment_category_id = name_to_id.get("Investment Category")
    if not wsjf_business_value_id:
        wsjf_business_value_id = name_to_id.get("Business Value")
    if not wsjf_job_size_id:
        wsjf_job_size_id = name_to_id.get("Job Size")
    if not wsjf_risk_opportunity_id:
        wsjf_risk_opportunity_id = name_to_id.get("Risk-Opportunity Value")
    if not wsjf_time_criticality_id:
        wsjf_time_criticality_id = name_to_id.get("Time Criticality")
    if not parent_link_id:
        parent_link_id = name_to_id.get("Parent Link")
    if not funded_by_id:
        funded_by_id = name_to_id.get("Funded By")
    if not estimated_id:
        estimated_id = name_to_id.get("Estimated")

    return {
        "story_points": story_points_id,
        "epic_name": epic_name_id,
        "epic_link": epic_link_id,
        "category": category_id,
        "investment_category": investment_category_id,
        "wsjf_business_value": wsjf_business_value_id,
        "wsjf_job_size": wsjf_job_size_id,
        "wsjf_risk_opportunity": wsjf_risk_opportunity_id,
        "wsjf_time_criticality": wsjf_time_criticality_id,
        "parent_link": parent_link_id,
        "funded_by": funded_by_id,
        "estimated": estimated_id,
    }


# Maps any casing/spacing/underscore variant → canonical snake_case key.
# Covers Title Case (legacy), lowercase with spaces, and snake_case inputs.
_CANONICAL_KEYS: Dict[str, str] = {
    "category": "category",
    "investment category": "investment_category",
    "investment_category": "investment_category",
    "business value": "business_value",
    "business_value": "business_value",
    "job size": "job_size",
    "job_size": "job_size",
    "risk-opportunity value": "risk_opportunity_value",
    "risk opportunity value": "risk_opportunity_value",
    "risk_opportunity_value": "risk_opportunity_value",
    "time criticality": "time_criticality",
    "time_criticality": "time_criticality",
    "parent link": "parent_link",
    "parent_link": "parent_link",
    "fix version/s": "fix_versions",
    "fix versions": "fix_versions",
    "fix_versions": "fix_versions",
    "funded by": "funded_by",
    "funded_by": "funded_by",
    "estimated": "estimated",
}


def normalize_ticket_keys(ticket: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for k, v in ticket.items():
        canonical = _CANONICAL_KEYS.get(k.lower(), k)
        normalized[canonical] = v
    return normalized


def build_fields(
    ticket: Dict[str, Any],
    project_key: str,
    special_ids: Dict[str, Optional[str]],
    epic_key_by_slug: Dict[str, str],
) -> Dict[str, Any]:
    issue_type = ticket["issue_type"]
    components = ticket.get("components", [])

    fields: Dict[str, Any] = {
        "project": {"key": ticket.get("project_key", project_key)},
        "issuetype": {"name": issue_type},
        "summary": ticket["summary"],
        "description": ticket.get("description", ""),
        "labels": ticket.get("labels", []),
    }

    if components:
        fields["components"] = [{"name": c} for c in components]

    if ticket.get("priority"):
        fields["priority"] = {"name": ticket["priority"]}

    if ticket.get("assignee_account_id"):
        fields["assignee"] = {"id": ticket["assignee_account_id"]}
    elif ticket.get("assignee_username"):
        fields["assignee"] = {"name": ticket["assignee_username"]}

    if ticket.get("story_points") is not None and special_ids.get("story_points"):
        fields[special_ids["story_points"]] = ticket["story_points"]

    if issue_type.lower() == "epic" and special_ids.get("epic_name"):
        fields[special_ids["epic_name"]] = ticket.get("epic_name", ticket["summary"])

    if issue_type.lower() == "epic" and ticket.get("parent_link") and special_ids.get("parent_link"):
        fields[special_ids["parent_link"]] = ticket["parent_link"]

    parent_slug = ticket.get("parent_epic_slug")
    if parent_slug:
        parent_key = epic_key_by_slug[parent_slug]
        # Epic Link for v2 compatibility; parent field only for sub-tasks
        if special_ids.get("epic_link"):
            fields[special_ids["epic_link"]] = parent_key
        elif issue_type.lower() == "sub-task":
            fields["parent"] = {"key": parent_key}

    if ticket.get("category") and special_ids.get("category"):
        fields[special_ids["category"]] = {"value": ticket["category"]}
    if ticket.get("investment_category") and special_ids.get("investment_category"):
        fields[special_ids["investment_category"]] = {"value": ticket["investment_category"]}

    for yaml_key, special_key in (
        ("business_value", "wsjf_business_value"),
        ("job_size", "wsjf_job_size"),
        ("risk_opportunity_value", "wsjf_risk_opportunity"),
        ("time_criticality", "wsjf_time_criticality"),
    ):
        if ticket.get(yaml_key) is not None and special_ids.get(special_key):
            fields[special_ids[special_key]] = ticket[yaml_key]

    fix_versions = ticket.get("fix_versions")
    if fix_versions is not None:
        versions = fix_versions if isinstance(fix_versions, list) else [fix_versions]
        fields["fixVersions"] = [{"name": str(v)} for v in versions]

    if ticket.get("funded_by") and special_ids.get("funded_by"):
        fields[special_ids["funded_by"]] = {"value": ticket["funded_by"]}

    if ticket.get("estimated") and special_ids.get("estimated"):
        fields[special_ids["estimated"]] = ticket["estimated"]
    elif ticket.get("estimated"):
        fields["timetracking"] = {"originalEstimate": ticket["estimated"]}

    return fields


def validate_update_schema(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if "tickets" not in data or not isinstance(data["tickets"], list) or not data["tickets"]:
        errors.append("'tickets' must be a non-empty list.")
        return errors

    for i, ticket in enumerate(data["tickets"], start=1):
        if not isinstance(ticket, dict):
            errors.append(f"tickets[{i}] must be an object.")
            continue

        if not ticket.get("key"):
            errors.append(f"tickets[{i}] missing required field 'key'.")

        if "story_points" in ticket and not isinstance(ticket["story_points"], (int, float)):
            errors.append(f"tickets[{i}] story_points must be a number.")

        if "labels" in ticket and not isinstance(ticket["labels"], list):
            errors.append(f"tickets[{i}] labels must be a list of strings.")

        components = ticket.get("components")
        if components is not None:
            if not isinstance(components, list) or any(not isinstance(c, str) for c in components):
                errors.append(f"tickets[{i}] components must be a list of strings.")

        if "assignee_account_id" in ticket and not isinstance(ticket["assignee_account_id"], str):
            errors.append(f"tickets[{i}] assignee_account_id must be a string.")

        if "assignee_username" in ticket and not isinstance(ticket["assignee_username"], str):
            errors.append(f"tickets[{i}] assignee_username must be a string.")

        if ticket.get("assignee_account_id") and ticket.get("assignee_username"):
            errors.append(f"tickets[{i}] use only one of assignee_account_id or assignee_username.")

    return errors


def build_update_fields(
    ticket: Dict[str, Any],
    special_ids: Dict[str, Optional[str]],
) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}

    for plain_key in ("summary", "description"):
        if plain_key in ticket:
            fields[plain_key] = ticket[plain_key]

    if "labels" in ticket:
        fields["labels"] = ticket["labels"]

    if ticket.get("priority"):
        fields["priority"] = {"name": ticket["priority"]}

    if "components" in ticket:
        fields["components"] = [{"name": c} for c in ticket["components"]]

    if ticket.get("assignee_account_id"):
        fields["assignee"] = {"id": ticket["assignee_account_id"]}
    elif ticket.get("assignee_username"):
        fields["assignee"] = {"name": ticket["assignee_username"]}

    if ticket.get("story_points") is not None and special_ids.get("story_points"):
        fields[special_ids["story_points"]] = ticket["story_points"]

    if ticket.get("epic_name") and special_ids.get("epic_name"):
        fields[special_ids["epic_name"]] = ticket["epic_name"]

    if ticket.get("category") and special_ids.get("category"):
        fields[special_ids["category"]] = {"value": ticket["category"]}
    if ticket.get("investment_category") and special_ids.get("investment_category"):
        fields[special_ids["investment_category"]] = {"value": ticket["investment_category"]}

    for yaml_key, special_key in (
        ("business_value", "wsjf_business_value"),
        ("job_size", "wsjf_job_size"),
        ("risk_opportunity_value", "wsjf_risk_opportunity"),
        ("time_criticality", "wsjf_time_criticality"),
    ):
        if ticket.get(yaml_key) is not None and special_ids.get(special_key):
            fields[special_ids[special_key]] = ticket[yaml_key]

    if ticket.get("parent_link") and special_ids.get("parent_link"):
        fields[special_ids["parent_link"]] = ticket["parent_link"]

    fix_versions = ticket.get("fix_versions")
    if fix_versions is not None:
        versions = fix_versions if isinstance(fix_versions, list) else [fix_versions]
        fields["fixVersions"] = [{"name": str(v)} for v in versions]

    if ticket.get("funded_by") and special_ids.get("funded_by"):
        fields[special_ids["funded_by"]] = {"value": ticket["funded_by"]}

    if ticket.get("estimated") and special_ids.get("estimated"):
        fields[special_ids["estimated"]] = ticket["estimated"]
    elif ticket.get("estimated"):
        fields["timetracking"] = {"originalEstimate": ticket["estimated"]}

    return fields


def split_epics_and_children(
    tickets: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    epics: List[Dict[str, Any]] = []
    children: List[Dict[str, Any]] = []
    for ticket in tickets:
        if str(ticket.get("issue_type", "")).lower() == "epic":
            epics.append(ticket)
        else:
            children.append(ticket)
    return epics, children


def flatten_created_keys(bulk_results: List[Dict[str, Any]]) -> List[str]:
    keys: List[str] = []
    for result in bulk_results:
        for issue in result.get("issues", []):
            if "key" in issue:
                keys.append(issue["key"])
    return keys


def resolve_assignee_usernames(
    tickets: List[Dict[str, Any]], client: Any, strict: bool = True
) -> List[Dict[str, Any]]:
    resolved: List[Dict[str, Any]] = []
    cache: Dict[str, Dict[str, str]] = {}

    for ticket in tickets:
        normalized = normalize_ticket_keys(ticket)
        username = normalized.get("assignee_username")

        if username and not normalized.get("assignee_account_id"):
            if username not in cache:
                try:
                    cache[username] = client.resolve_assignee(username)
                except ValueError:
                    if strict:
                        raise
                    print(
                        f"Warning: Could not resolve assignee_username '{username}' in dry-run; "
                        "assignee will be omitted."
                    )
                    cache[username] = {}

            info = cache[username]
            if info:
                if info["type"] == "id":
                    normalized["assignee_account_id"] = info["value"]
                else:
                    normalized["assignee_username"] = info["value"]

        resolved.append(normalized)

    return resolved
