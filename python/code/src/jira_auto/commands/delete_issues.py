import argparse
import sys

from ..client import JiraApiError, JiraClient
from ..config import build_config_from_env
from ..models import load_yaml


def cmd_delete_issues(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)

    if "keys" not in data or not isinstance(data["keys"], list) or not data["keys"]:
        raise ValueError("'keys' must be a non-empty list of issue keys.")

    keys = data["keys"]
    for key in keys:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Each key must be a non-empty string.")

    if args.dry_run:
        print(f"Dry-run: Would delete {len(keys)} ticket(s):")
        for key in keys:
            print(f"  - {key}")
        return 0

    config = build_config_from_env(data)
    client = JiraClient(config)

    deleted = []
    failed = []

    for key in keys:
        try:
            key = key.strip()
            print(f"Deleting {key}...", end=" ")
            client.delete(key)
            deleted.append(key)
            print("OK")
        except JiraApiError as e:
            failed.append((key, str(e)))
            print(f"FAILED: {e}", file=sys.stderr)

    print("\nDelete complete.")
    print(f"Deleted ({len(deleted)}): {deleted}")
    if failed:
        print(f"Failed ({len(failed)}):")
        for key, error in failed:
            print(f"  - {key}: {error}")
        return 1
    return 0
