from unittest.mock import MagicMock, patch

import pytest

from jira_auto.client import JiraApiError, JiraClient
from jira_auto.config import JiraConfig


@pytest.fixture
def cloud_config():
    return JiraConfig(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token-12345678901234",
        default_project_key="ENG",
    )


@pytest.fixture
def dc_config():
    return JiraConfig(
        base_url="https://jira.example.com",
        email="test@example.com",
        api_token="test-token-12345678901234",
        default_project_key="ENG",
    )


def test_cloud_uses_basic_auth(cloud_config):
    client = JiraClient(cloud_config)
    assert client.session.auth == ("test@example.com", "test-token-12345678901234")


def test_dc_uses_bearer_auth(dc_config):
    client = JiraClient(dc_config)
    assert client.session.headers["Authorization"] == "Bearer test-token-12345678901234"


def test_parse_json_raises_on_html(cloud_config):
    client = JiraClient(cloud_config)
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.status_code = 401
    with pytest.raises(JiraApiError, match="HTML page"):
        client._parse_json(mock_response, "GET", "/test")


def test_get_fields_returns_name_to_id_map(cloud_config):
    client = JiraClient(cloud_config)
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {"name": "Story Points", "id": "customfield_10016"},
        {"name": "Epic Link", "id": "customfield_10014"},
    ]
    with patch.object(client.session, "get", return_value=mock_response):
        fields = client.get_fields()
    assert fields["Story Points"] == "customfield_10016"
    assert fields["Epic Link"] == "customfield_10014"


def test_resolve_assignee_prefers_exact_display_name_match(cloud_config):
    client = JiraClient(cloud_config)
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {"displayName": "Jane Doe Smith", "accountId": "wrong-id"},
        {"displayName": "Jane Doe", "accountId": "correct-id"},
    ]
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.resolve_assignee("Jane Doe")
    assert result == {"type": "id", "value": "correct-id"}
