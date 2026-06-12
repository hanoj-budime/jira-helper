import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class JiraConfig:
    base_url: str
    email: str
    api_token: str
    default_project_key: str


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


def build_config_from_env(data: Dict[str, Any], require_project_key: bool = True) -> JiraConfig:
    base_url = os.getenv("JIRA_BASE_URL", "").strip()
    email = os.getenv("JIRA_EMAIL", "").strip()
    token = os.getenv("JIRA_API_TOKEN", "").strip()

    missing = [
        name
        for name, value in [("JIRA_BASE_URL", base_url), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)]
        if not value
    ]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))

    if len(token) < 20:
        raise ValueError(
            f"JIRA_API_TOKEN appears too short ({len(token)} chars). "
            "Did you copy the full token value from Jira (not just the token name)?"
        )

    default_project_key = data.get("project_key", os.getenv("JIRA_PROJECT_KEY", ""))
    if require_project_key and not default_project_key:
        raise ValueError("Missing project key in YAML and JIRA_PROJECT_KEY env var.")

    return JiraConfig(
        base_url=base_url.rstrip("/"),
        email=email,
        api_token=token,
        default_project_key=default_project_key,
    )
