import argparse
import sys
from pathlib import Path

from .client import JiraApiError
from .commands.create_issues import cmd_apply, cmd_create_issues, cmd_dry_run, cmd_validate
from .commands.delete_issues import cmd_delete_issues
from .commands.init import cmd_init
from .commands.update_issues import cmd_update_issues
from .config import load_dotenv_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jira-auto",
        description="Create Jira Epics and Issues in bulk from YAML.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── Canonical commands ──────────────────────────────────────────────────

    init_parser = subparsers.add_parser("init", help="Generate a starter YAML template.")
    init_parser.add_argument(
        "--output",
        default="tickets.yaml",
        metavar="FILE",
        help="Output template file path (default: tickets.yaml).",
    )
    init_parser.set_defaults(func=cmd_init)

    ci_parser = subparsers.add_parser(
        "create-issues",
        help="Validate, preview, or create Jira issues from a YAML file.",
    )
    ci_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    ci_parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate schema only; do not call Jira APIs.",
    )
    ci_parser.add_argument(
        "--check-jira",
        action="store_true",
        help="With --validate-only: also query Jira to verify custom-field discovery.",
    )
    ci_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview generated Jira payloads without creating tickets.",
    )
    ci_parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        metavar="N",
        help="Bulk-create batch size (default: 50). Ignored with --validate-only or --dry-run.",
    )
    ci_parser.set_defaults(func=cmd_create_issues)

    di_parser = subparsers.add_parser("delete-issues", help="Delete Jira tickets listed in a YAML file.")
    di_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file with issue keys to delete.")
    di_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions without deleting.",
    )
    di_parser.set_defaults(func=cmd_delete_issues)

    ui_parser = subparsers.add_parser("update-issues", help="Update existing Jira issues from a YAML file.")
    ui_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    ui_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview update payloads without writing to Jira.",
    )
    ui_parser.set_defaults(func=cmd_update_issues)

    # ── Legacy commands (kept for backward compatibility) ───────────────────

    create_parser = subparsers.add_parser("create", help="[legacy: use init] Generate a starter YAML template.")
    create_parser.add_argument(
        "--output",
        default="tickets.yaml",
        metavar="FILE",
        help="Output template file path (default: tickets.yaml).",
    )
    create_parser.set_defaults(func=cmd_init)

    validate_parser = subparsers.add_parser(
        "validate",
        help="[legacy: use create-issues --validate-only] Validate YAML input schema.",
    )
    validate_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    validate_parser.add_argument(
        "--check-jira",
        action="store_true",
        help="Also query Jira fields to verify custom-field discovery.",
    )
    validate_parser.set_defaults(func=cmd_validate)

    dry_run_parser = subparsers.add_parser(
        "dry-run",
        help="[legacy: use create-issues --dry-run] Preview generated Jira payloads.",
    )
    dry_run_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    dry_run_parser.set_defaults(func=cmd_dry_run)

    apply_parser = subparsers.add_parser(
        "apply",
        help="[legacy: use create-issues] Create Jira tickets in bulk.",
    )
    apply_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    apply_parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        metavar="N",
        help="Bulk create batch size (default: 50).",
    )
    apply_parser.set_defaults(func=cmd_apply)

    delete_parser = subparsers.add_parser(
        "delete",
        help="[legacy: use delete-issues] Delete Jira tickets by key.",
    )
    delete_parser.add_argument(
        "--input",
        required=True,
        metavar="FILE",
        help="Input YAML file with issue keys to delete.",
    )
    delete_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions without actually deleting.",
    )
    delete_parser.set_defaults(func=cmd_delete_issues)

    update_parser = subparsers.add_parser(
        "update",
        help="[legacy: use update-issues] Update existing Jira issues.",
    )
    update_parser.add_argument("--input", required=True, metavar="FILE", help="Input YAML file path.")
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview update payloads without writing to Jira.",
    )
    update_parser.set_defaults(func=cmd_update_issues)

    return parser


def main() -> int:
    load_dotenv_file(Path.cwd() / "environments" / ".env")

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
