# Jira Helper

Utilities for working with Jira in two modes:

- JavaScript browser-console snippets for fast data extraction from Jira UI pages.
- Python CLI for validating and bulk-creating Jira tickets from YAML.

## Project Layout

```text
javascript/
  README.md
  code/
python/
  README.md
  code/
```

## Quick Start

### JavaScript snippets

1. Open Jira page (board, epic view, or search results).
2. Open browser developer console.
3. Paste one script from `javascript/code/` and run it.
4. Read the `console.table(...)` output.

### Python CLI

1. Install dependencies:

```powershell
python -m pip install -r python/code/requirements.txt
```

2. Create `python/code/.env` from `python/code/.env.example` and fill values.
3. Use the CLI commands documented in `python/README.md`.

## Notes

- Keep `python/code/.env` out of version control.
- Use `python/code/tickets.example.yaml` as a safe template.