import time
from typing import Any, Dict, List, Optional

import requests

from .config import JiraConfig


class JiraApiError(Exception):
    pass


class JiraClient:
    def __init__(self, config: JiraConfig):
        self.config = config
        self.session = requests.Session()
        # Jira Cloud (*.atlassian.net) uses Basic Auth; Data Center/Server uses Bearer token.
        if "atlassian.net" in config.base_url:
            self.session.auth = (config.email, config.api_token)
        else:
            self.session.headers["Authorization"] = f"Bearer {config.api_token}"
        self.session.headers["Accept"] = "application/json"

    def _parse_json(self, response: requests.Response, method: str, path: str) -> Any:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            raise JiraApiError(
                f"{method} {path} returned an HTML page (status {response.status_code}). "
                "This usually means authentication failed. "
                "Check that your JIRA_API_TOKEN is a valid, non-expired Personal Access Token."
            )
        try:
            return response.json()
        except ValueError:
            preview = response.text[:200].replace("\n", " ")
            raise JiraApiError(
                f"{method} {path} returned non-JSON (status {response.status_code}). "
                f"Content-Type: {content_type}. Body preview: {preview!r}"
            )

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.config.base_url}{path}"
        response = self.session.get(url, params=params, timeout=30)
        if not response.ok:
            raise JiraApiError(f"GET {path} failed: {response.status_code} {response.text}")
        return self._parse_json(response, "GET", path)

    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.config.base_url}{path}"
        response = self.session.post(
            url, json=payload, timeout=30, headers={"Content-Type": "application/json"}
        )
        if not response.ok:
            raise JiraApiError(f"POST {path} failed: {response.status_code} {response.text}")
        return self._parse_json(response, "POST", path)

    def delete(self, key: str) -> None:
        key = key.strip()
        try:
            url = f"{self.config.base_url}/rest/api/3/issues/{key}"
            response = self.session.delete(url, timeout=30)
            if response.ok or response.status_code == 204:
                return
            if response.status_code != 404:
                raise JiraApiError(f"DELETE /rest/api/3/issues/{key} failed: {response.status_code}")
        except JiraApiError as e:
            if "404" not in str(e):
                raise

        # Fall back to v2 with alternate endpoint spellings
        endpoints = [
            f"/rest/api/2/issues/{key}",
            f"/rest/api/2/issue/{key}",
        ]
        for endpoint in endpoints:
            try:
                url = f"{self.config.base_url}{endpoint}"
                response = self.session.delete(url, timeout=30)
                if response.ok or response.status_code == 204:
                    return
                if response.status_code == 404 and endpoint == endpoints[-1]:
                    raise JiraApiError(f"DELETE {key} failed: Issue not found (404)")
            except Exception:
                if endpoint == endpoints[-1]:
                    raise JiraApiError(f"DELETE {key} failed: {response.status_code} {response.text}")

    def get_fields(self) -> Dict[str, str]:
        try:
            fields = self.get("/rest/api/3/field")
        except JiraApiError:
            fields = self.get("/rest/api/2/field")
        return {field["name"]: field["id"] for field in fields}

    def resolve_assignee(self, assignee_username: str) -> Dict[str, str]:
        try:
            users = self.get("/rest/api/3/user/search", params={"query": assignee_username, "maxResults": 20})
        except JiraApiError:
            users = self.get("/rest/api/2/user/search", params={"username": assignee_username, "maxResults": 20})

        if not isinstance(users, list) or not users:
            raise ValueError(f"No Jira user found for assignee_username '{assignee_username}'.")

        exact_match = None
        for user in users:
            if str(user.get("displayName", "")).strip().lower() == assignee_username.strip().lower():
                exact_match = user
                break

        selected = exact_match or users[0]
        if "accountId" in selected:
            return {"type": "id", "value": selected["accountId"]}
        elif "name" in selected:
            return {"type": "name", "value": selected["name"]}
        else:
            raise ValueError(
                f"Jira user returned neither accountId nor name for assignee_username '{assignee_username}'."
            )

    def put(self, path: str, payload: Dict[str, Any]) -> None:
        url = f"{self.config.base_url}{path}"
        response = self.session.put(
            url, json=payload, timeout=30, headers={"Content-Type": "application/json"}
        )
        if not response.ok:
            raise JiraApiError(f"PUT {path} failed: {response.status_code} {response.text}")

    def update_issue(self, key: str, fields: Dict[str, Any]) -> None:
        key = key.strip()
        try:
            self.put(f"/rest/api/3/issue/{key}", {"fields": fields})
        except JiraApiError:
            self.put(f"/rest/api/2/issue/{key}", {"fields": fields})

    def create_issues_bulk(
        self, field_payloads: List[Dict[str, Any]], batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for idx in range(0, len(field_payloads), batch_size):
            chunk = field_payloads[idx : idx + batch_size]
            payload = {"issueUpdates": [{"fields": fields} for fields in chunk]}
            try:
                result = self.post("/rest/api/3/issue/bulk", payload)
            except JiraApiError:
                result = self.post("/rest/api/2/issue/bulk", payload)
            results.append(result)
            time.sleep(0.2)
        return results
