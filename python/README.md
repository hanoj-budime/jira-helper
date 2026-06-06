# Jira Automation CLI

Production-ready starter CLI for bulk Jira ticket creation from YAML.

## Commands

- `create`: generate a starter input template
- `validate`: validate input schema locally (and optionally Jira field discovery)
- `dry-run`: print Jira payloads without creating issues
- `apply`: create Epics first, then children in bulk

## Setup

1. Install dependencies:

```powershell
python -m pip install -r code/requirements.txt
```

2. Create and configure environment variables:

```powershell
copy code/.env.example code/.env
```

Then edit `code/.env`:

```dotenv
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=ENG
```

Optional overrides for custom fields:

```dotenv
JIRA_STORY_POINTS_FIELD_ID=customfield_10016
JIRA_EPIC_NAME_FIELD_ID=customfield_10011
JIRA_EPIC_LINK_FIELD_ID=customfield_10014
```

The CLI automatically loads `code/.env` when it starts.

## Usage

Generate template:

```powershell
python code/jira_cli.py create --output code/tickets.yaml
```

Validate only:

```powershell
python code/jira_cli.py validate --input code/tickets.yaml
```

Validate + check Jira field discovery:

```powershell
python code/jira_cli.py validate --input code/tickets.yaml --check-jira
```

Preview payload:

```powershell
python code/jira_cli.py dry-run --input code/tickets.yaml
```

Create tickets:

```powershell
python code/jira_cli.py apply --input code/tickets.yaml --batch-size 50
```

## Input Template Notes

- Each Epic must have a unique `slug`.
- Child tickets use `parent_epic_slug` to attach to an Epic.
- For Jira Cloud, assignee should be `assignee_account_id`.
- Story points and Epic fields often require custom field IDs.
