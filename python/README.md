# Jira Automation CLI

Production-ready CLI for bulk Jira issue creation and deletion from YAML.

## Installation

```bash
pip install -e ".[dev]"
```

## Setup

Copy `environments/.env.example` to `environments/.env` and fill in your credentials:

```bash
cp environments/.env.example environments/.env
```

```dotenv
JIRA_BASE_URL=https://jira.example.com
JIRA_EMAIL=username@example.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=ENG
```

Optional overrides for custom fields (if auto-discovery fails):

```dotenv
JIRA_STORY_POINTS_FIELD_ID=customfield_10016
JIRA_EPIC_NAME_FIELD_ID=customfield_10011
JIRA_EPIC_LINK_FIELD_ID=customfield_10014
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Generate a starter YAML template |
| `create-issues` | Validate, preview, or create Jira issues from a YAML file |
| `update-issues` | Validate, preview, or update existing Jira issues from a YAML file |
| `delete-issues` | Delete issues by key |

## Usage

**Generate template:**
```bash
python -m jira_auto init --output templates/create_issues.yaml
```

**Create issues: (validate only, no API calls, then check Jira references)**
```bash
python -m jira_auto create-issues --input templates/create_issues.yaml --validate-only
python -m jira_auto create-issues --input templates/create_issues.yaml --validate-only --check-jira
```

**Create issues (preview first, then execute):**
```bash
python -m jira_auto create-issues --input templates/create_issues.yaml --dry-run
python -m jira_auto create-issues --input templates/create_issues.yaml
python -m jira_auto create-issues --input templates/create_issues.yaml --batch-size 100
```

**Update issues: (preview first, then execute)**
```bash
python -m jira_auto update-issues --input templates/update_issues.yaml --dry-run
python -m jira_auto update-issues --input templates/update_issues.yaml
```

**Delete issues: (preview first, then execute)**
```bash
python -m jira_auto delete-issues --input templates/delete_issues.yaml --dry-run
python -m jira_auto delete-issues --input templates/delete_issues.yaml
```

## YAML Format

See [`templates/create_issues.yaml`](templates/create_issues.yaml) for a full annotated example.

Key rules:
- Each Epic must have a unique `slug`
- Child issues reference their Epic via `parent_epic_slug`
- Use `assignee_username` (display name) — the CLI resolves it to a Jira `accountId` automatically
- Use `assignee_account_id` for direct assignment (skips resolution)
- `components` is a list of Jira component names

### Delete Format

```yaml
keys:
  - "YOUR_PROJECT_KEY-1"
  - "YOUR_PROJECT_KEY-2"
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
# For verbose output:
pytest -v
# Coverage output:
pytest --cov=src/jira_auto tests/

# Lint
ruff check src/ tests/
```

## Project Structure

```
src/jira_auto/
├── cli.py          # Entry point and argument parser
├── config.py       # Env var loading and JiraConfig
├── client.py       # Jira REST API client
├── models.py       # Schema validation, field building, helpers
└── commands/
    ├── init.py           # Template generation (init)
    ├── create_issues.py  # Validate, dry-run, and bulk create (create-issues)
    ├── update_issues.py  # Validate, dry-run, and bulk update (update-issues)
    └── delete_issues.py  # Issue deletion (delete-issues)
```
