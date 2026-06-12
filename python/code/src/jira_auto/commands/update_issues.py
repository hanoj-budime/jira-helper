import argparse
import json

from ..client import JiraClient
from ..config import build_config_from_env
from ..models import (
    build_update_fields,
    infer_field_ids,
    load_yaml,
    resolve_assignee_usernames,
    validate_update_schema,
)


def _print_errors(errors: list) -> None:
    print("Validation failed:")
    for err in errors:
        print(f"  - {err}")


def cmd_update_issues(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    errors = validate_update_schema(data)
    if errors:
        _print_errors(errors)
        return 1

    config = build_config_from_env(data, require_project_key=False)
    client = JiraClient(config)
    name_to_id = client.get_fields()
    special_ids = infer_field_ids(name_to_id)

    tickets = resolve_assignee_usernames(data["tickets"], client, strict=not args.dry_run)

    if args.dry_run:
        payloads = {t["key"]: build_update_fields(t, special_ids) for t in tickets}
        print(json.dumps(payloads, indent=2))
        return 0

    updated = []
    failed = []
    for ticket in tickets:
        key = ticket["key"].strip()
        fields = build_update_fields(ticket, special_ids)
        if not fields:
            print(f"  Skipped {key}: no fields to update.")
            continue
        try:
            client.update_issue(key, fields)
            print(f"  Updated {key}")
            updated.append(key)
        except Exception as exc:
            print(f"  Failed  {key}: {exc}")
            failed.append(key)

    print(f"\nUpdate complete. Updated ({len(updated)}): {updated}")
    if failed:
        print(f"Failed ({len(failed)}): {failed}")
        return 1
    return 0
