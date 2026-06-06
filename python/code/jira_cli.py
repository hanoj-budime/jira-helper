import argparse
import json
import os
from pathlib import Path
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml


class JiraApiError(Exception):
    pass


def load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    with dotenv_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


@dataclass
class JiraConfig:
    base_url: str
    email: str
    api_token: str
    default_project_key: str


class JiraClient:
    def __init__(self, config: JiraConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.email, config.api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.config.base_url}{path}"
        response = self.session.get(url, params=params, timeout=30)
        if not response.ok:
            raise JiraApiError(f"GET {path} failed: {response.status_code} {response.text}")
        return response.json()

    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.config.base_url}{path}"
        response = self.session.post(url, json=payload, timeout=30)
        if not response.ok:
            raise JiraApiError(f"POST {path} failed: {response.status_code} {response.text}")
        return response.json()

    def get_fields(self) -> Dict[str, str]:
        fields = self.get("/rest/api/3/field")
        return {field["name"]: field["id"] for field in fields}

    def create_issues_bulk(self, field_payloads: List[Dict[str, Any]], batch_size: int = 50) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for idx in range(0, len(field_payloads), batch_size):
            chunk = field_payloads[idx : idx + batch_size]
            payload = {"issueUpdates": [{"fields": fields} for fields in chunk]}
            result = self.post("/rest/api/3/issue/bulk", payload)
            results.append(result)
            # Small pause to avoid throttling on large runs.
            time.sleep(0.2)
        return results


def to_adf_paragraph(text: str) -> Dict[str, Any]:
    lines = text.splitlines() or [""]
    content: List[Dict[str, Any]] = []
    for line in lines:
        content.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line}],
            }
        )
    return {
        "type": "doc",
        "version": 1,
        "content": content,
    }


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
                "assignee_account_id": "5b10a2844c20165700ede21g",
            },
            {
                "issue_type": "Story",
                "summary": "Implement SAML login",
                "description": "As an enterprise user, I can log in with my IdP.",
                "priority": "High",
                "labels": ["security", "saml"],
                "story_points": 8,
                "assignee_account_id": "5b10a2844c20165700ede21g",
                "parent_epic_slug": "epic-auth",
            },
            {
                "issue_type": "Task",
                "summary": "Add login observability dashboard",
                "description": "Track login success, latency, and failure classes.",
                "priority": "Medium",
                "labels": ["auth", "observability"],
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

    slugs = set()
    epic_slugs = set()

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

    # Validate parent references after all epics are known.
    for i, ticket in enumerate(data["tickets"], start=1):
        parent = ticket.get("parent_epic_slug")
        if parent and parent not in epic_slugs:
            errors.append(f"tickets[{i}] parent_epic_slug '{parent}' does not match any Epic slug.")

    return errors


def infer_field_ids(name_to_id: Dict[str, str]) -> Dict[str, Optional[str]]:
    # Field names vary between Jira setups. Try common labels and allow env overrides.
    story_points_id = os.getenv("JIRA_STORY_POINTS_FIELD_ID")
    epic_name_id = os.getenv("JIRA_EPIC_NAME_FIELD_ID")
    epic_link_id = os.getenv("JIRA_EPIC_LINK_FIELD_ID")

    if not story_points_id:
        story_points_id = name_to_id.get("Story Points") or name_to_id.get("Story point estimate")
    if not epic_name_id:
        epic_name_id = name_to_id.get("Epic Name")
    if not epic_link_id:
        epic_link_id = name_to_id.get("Epic Link")

    return {
        "story_points": story_points_id,
        "epic_name": epic_name_id,
        "epic_link": epic_link_id,
    }


def build_fields(
    ticket: Dict[str, Any],
    project_key: str,
    special_ids: Dict[str, Optional[str]],
    epic_key_by_slug: Dict[str, str],
) -> Dict[str, Any]:
    issue_type = ticket["issue_type"]

    fields: Dict[str, Any] = {
        "project": {"key": ticket.get("project_key", project_key)},
        "issuetype": {"name": issue_type},
        "summary": ticket["summary"],
        "description": to_adf_paragraph(ticket.get("description", "")),
        "labels": ticket.get("labels", []),
    }

    if ticket.get("priority"):
        fields["priority"] = {"name": ticket["priority"]}

    if ticket.get("assignee_account_id"):
        fields["assignee"] = {"id": ticket["assignee_account_id"]}

    if ticket.get("story_points") is not None and special_ids.get("story_points"):
        fields[special_ids["story_points"]] = ticket["story_points"]

    if issue_type.lower() == "epic" and special_ids.get("epic_name"):
        fields[special_ids["epic_name"]] = ticket.get("epic_name", ticket["summary"])

    parent_slug = ticket.get("parent_epic_slug")
    if parent_slug:
        parent_key = epic_key_by_slug[parent_slug]
        # Parent is preferred for modern hierarchy endpoints.
        fields["parent"] = {"key": parent_key}
        # Epic Link is kept for compatibility with older company-managed setups.
        if special_ids.get("epic_link"):
            fields[special_ids["epic_link"]] = parent_key

    return fields


def split_epics_and_children(tickets: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
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


def cmd_create(args: argparse.Namespace) -> int:
    if os.path.exists(args.output):
        print(f"Refusing to overwrite existing file: {args.output}", file=sys.stderr)
        return 2
    write_create_template(args.output)
    print(f"Template created: {args.output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_local_schema(data)

    if args.check_jira:
        config = build_config_from_env(data)
        client = JiraClient(config)
        name_to_id = client.get_fields()
        special_ids = infer_field_ids(name_to_id)
        if not special_ids.get("story_points"):
            print("Warning: Story Points field id not found automatically.")
        if not special_ids.get("epic_name"):
            print("Warning: Epic Name field id not found automatically.")

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation passed.")
    return 0


def cmd_dry_run(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_local_schema(data)
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    config = build_config_from_env(data)
    client = JiraClient(config)
    name_to_id = client.get_fields()
    special_ids = infer_field_ids(name_to_id)

    project_key = data.get("project_key", config.default_project_key)
    tickets = data["tickets"]
    epics, children = split_epics_and_children(tickets)

    epic_payloads = [build_fields(ticket, project_key, special_ids, {}) for ticket in epics]

    # Fake predictable keys for previewing child links.
    fake_epic_keys = {}
    for idx, epic in enumerate(epics, start=1):
        fake_epic_keys[epic["slug"]] = f"{project_key}-EPIC-{idx}"

    child_payloads = [build_fields(ticket, project_key, special_ids, fake_epic_keys) for ticket in children]

    print(json.dumps({"epics": epic_payloads, "children": child_payloads}, indent=2))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_local_schema(data)
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    config = build_config_from_env(data)
    client = JiraClient(config)

    name_to_id = client.get_fields()
    special_ids = infer_field_ids(name_to_id)

    project_key = data.get("project_key", config.default_project_key)
    tickets = data["tickets"]
    epics, children = split_epics_and_children(tickets)

    epic_payloads = [build_fields(ticket, project_key, special_ids, {}) for ticket in epics]
    epic_key_by_slug: Dict[str, str] = {}

    if epic_payloads:
        epic_results = client.create_issues_bulk(epic_payloads, batch_size=args.batch_size)
        epic_keys = flatten_created_keys(epic_results)
        if len(epic_keys) != len(epics):
            print("Warning: Number of created Epic keys does not match Epic count.")
        for idx, epic in enumerate(epics):
            if idx < len(epic_keys):
                epic_key_by_slug[epic["slug"]] = epic_keys[idx]

    child_payloads = [build_fields(ticket, project_key, special_ids, epic_key_by_slug) for ticket in children]
    child_results: List[Dict[str, Any]] = []
    if child_payloads:
        child_results = client.create_issues_bulk(child_payloads, batch_size=args.batch_size)

    created_epics = list(epic_key_by_slug.values())
    created_children = flatten_created_keys(child_results)

    print("Apply complete.")
    print(f"Created Epics ({len(created_epics)}): {created_epics}")
    print(f"Created Children ({len(created_children)}): {created_children}")
    return 0


def build_config_from_env(data: Dict[str, Any]) -> JiraConfig:
    base_url = os.getenv("JIRA_BASE_URL", "").strip()
    email = os.getenv("JIRA_EMAIL", "").strip()
    token = os.getenv("JIRA_API_TOKEN", "").strip()

    missing = [name for name, value in [("JIRA_BASE_URL", base_url), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)] if not value]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))

    default_project_key = data.get("project_key", os.getenv("JIRA_PROJECT_KEY", ""))
    if not default_project_key:
        raise ValueError("Missing project key in YAML and JIRA_PROJECT_KEY env var.")

    return JiraConfig(
        base_url=base_url.rstrip("/"),
        email=email,
        api_token=token,
        default_project_key=default_project_key,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jira-cli",
        description="Create Jira Epics and Issues in bulk from YAML.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Generate a starter YAML template.")
    create_parser.add_argument("--output", default="tickets.yaml", help="Output template file path.")
    create_parser.set_defaults(func=cmd_create)

    validate_parser = subparsers.add_parser("validate", help="Validate YAML input schema.")
    validate_parser.add_argument("--input", required=True, help="Input YAML file path.")
    validate_parser.add_argument(
        "--check-jira",
        action="store_true",
        help="Also query Jira fields to verify custom-field discovery.",
    )
    validate_parser.set_defaults(func=cmd_validate)

    dry_run_parser = subparsers.add_parser("dry-run", help="Preview generated Jira payloads.")
    dry_run_parser.add_argument("--input", required=True, help="Input YAML file path.")
    dry_run_parser.set_defaults(func=cmd_dry_run)

    apply_parser = subparsers.add_parser("apply", help="Create Jira tickets in bulk.")
    apply_parser.add_argument("--input", required=True, help="Input YAML file path.")
    apply_parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Bulk create batch size. Default: 50.",
    )
    apply_parser.set_defaults(func=cmd_apply)

    return parser


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    load_dotenv_file(script_dir / ".env")

    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except JiraApiError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
