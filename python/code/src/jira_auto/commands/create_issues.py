import argparse
import json
from typing import Dict, List

from ..client import JiraClient
from ..config import build_config_from_env
from ..models import (
    build_fields,
    flatten_created_keys,
    infer_field_ids,
    load_yaml,
    resolve_assignee_usernames,
    split_epics_and_children,
    validate_local_schema,
)


def _print_errors(errors: list) -> None:
    print("Validation failed:")
    for err in errors:
        print(f"  - {err}")


def _run_validate(args: argparse.Namespace) -> int:
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
        _print_errors(errors)
        return 1

    print("Validation passed.")
    return 0


def _run_dry_run(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_local_schema(data)
    if errors:
        _print_errors(errors)
        return 1

    config = build_config_from_env(data)
    client = JiraClient(config)
    name_to_id = client.get_fields()
    special_ids = infer_field_ids(name_to_id)

    project_key = data.get("project_key", config.default_project_key)
    tickets = resolve_assignee_usernames(data["tickets"], client, strict=False)
    epics, children = split_epics_and_children(tickets)

    epic_payloads = [build_fields(ticket, project_key, special_ids, {}) for ticket in epics]
    # Predictable fake keys so child epic-link fields are previewable
    fake_epic_keys = {epic["slug"]: f"{project_key}-EPIC-{i}" for i, epic in enumerate(epics, start=1)}
    child_payloads = [build_fields(ticket, project_key, special_ids, fake_epic_keys) for ticket in children]

    print(json.dumps({"epics": epic_payloads, "children": child_payloads}, indent=2))
    return 0


def _run_apply(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_local_schema(data)
    if errors:
        _print_errors(errors)
        return 1

    config = build_config_from_env(data)
    client = JiraClient(config)
    name_to_id = client.get_fields()
    special_ids = infer_field_ids(name_to_id)

    project_key = data.get("project_key", config.default_project_key)
    tickets = resolve_assignee_usernames(data["tickets"], client)
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
    child_results: List = []
    if child_payloads:
        child_results = client.create_issues_bulk(child_payloads, batch_size=args.batch_size)

    created_epics = list(epic_key_by_slug.values())
    created_children = flatten_created_keys(child_results)

    print("Create complete.")
    print(f"Created Epics ({len(created_epics)}): {created_epics}")
    print(f"Created Children ({len(created_children)}): {created_children}")
    return 0


def cmd_create_issues(args: argparse.Namespace) -> int:
    if args.validate_only:
        return _run_validate(args)
    if args.dry_run:
        return _run_dry_run(args)
    return _run_apply(args)


# Legacy aliases — used by the deprecated validate / dry-run / apply subcommands.
cmd_validate = _run_validate
cmd_dry_run = _run_dry_run
cmd_apply = _run_apply
