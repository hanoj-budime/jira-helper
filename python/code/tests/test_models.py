
from jira_auto.models import (
    build_fields,
    flatten_created_keys,
    infer_field_ids,
    split_epics_and_children,
    validate_local_schema,
)


def test_validate_passes_valid_data(yaml_data):
    assert validate_local_schema(yaml_data) == []


def test_validate_fails_missing_summary():
    data = {"tickets": [{"issue_type": "Story"}]}
    errors = validate_local_schema(data)
    assert any("summary" in e for e in errors)


def test_validate_fails_missing_epic_slug():
    data = {"tickets": [{"issue_type": "Epic", "summary": "No slug"}]}
    errors = validate_local_schema(data)
    assert any("slug" in e for e in errors)


def test_validate_fails_duplicate_slug():
    data = {
        "tickets": [
            {"slug": "epic-1", "issue_type": "Epic", "summary": "First"},
            {"slug": "epic-1", "issue_type": "Epic", "summary": "Second"},
        ]
    }
    errors = validate_local_schema(data)
    assert any("duplicate slug" in e for e in errors)


def test_validate_fails_bad_parent_ref():
    data = {
        "tickets": [
            {"issue_type": "Story", "summary": "Orphan", "parent_epic_slug": "nonexistent"},
        ]
    }
    errors = validate_local_schema(data)
    assert any("parent_epic_slug" in e for e in errors)


def test_validate_fails_conflicting_assignee_fields():
    data = {
        "tickets": [
            {
                "issue_type": "Story",
                "summary": "Story",
                "assignee_account_id": "abc123",
                "assignee_username": "jane",
            }
        ]
    }
    errors = validate_local_schema(data)
    assert any("assignee" in e for e in errors)


def test_split_epics_and_children(yaml_data):
    epics, children = split_epics_and_children(yaml_data["tickets"])
    assert len(epics) == 1
    assert len(children) == 2


def test_flatten_created_keys():
    results = [
        {"issues": [{"key": "ENG-1"}, {"key": "ENG-2"}]},
        {"issues": [{"key": "ENG-3"}]},
    ]
    assert flatten_created_keys(results) == ["ENG-1", "ENG-2", "ENG-3"]


def test_flatten_created_keys_empty():
    assert flatten_created_keys([]) == []
    assert flatten_created_keys([{"issues": []}]) == []


def test_build_fields_basic(yaml_data):
    ticket = yaml_data["tickets"][2]  # Task: priority Medium
    fields = build_fields(ticket, "ENG", {}, {"epic-auth": "ENG-1"})
    assert fields["summary"] == "Add login observability dashboard"
    assert fields["priority"] == {"name": "Medium"}
    assert fields["project"] == {"key": "ENG"}


def test_build_fields_components(yaml_data):
    ticket = yaml_data["tickets"][0]  # Epic: components=[Authentication]
    fields = build_fields(ticket, "ENG", {}, {})
    assert fields["components"] == [{"name": "Authentication"}]


def test_build_fields_story_points(yaml_data):
    ticket = yaml_data["tickets"][1]  # Story: story_points=8
    special_ids = {"story_points": "customfield_10016", "epic_name": None, "epic_link": None,
                   "category": None, "investment_category": None}
    fields = build_fields(ticket, "ENG", special_ids, {"epic-auth": "ENG-1"})
    assert fields["customfield_10016"] == 8


def test_build_fields_epic_link(yaml_data):
    ticket = yaml_data["tickets"][1]  # Story: parent_epic_slug=epic-auth
    special_ids = {"story_points": None, "epic_name": None, "epic_link": "customfield_10014",
                   "category": None, "investment_category": None}
    fields = build_fields(ticket, "ENG", special_ids, {"epic-auth": "ENG-10"})
    assert fields["customfield_10014"] == "ENG-10"


def test_infer_field_ids_from_map():
    name_to_id = {
        "Story Points": "customfield_10016",
        "Epic Name": "customfield_10011",
        "Epic Link": "customfield_10014",
    }
    ids = infer_field_ids(name_to_id)
    assert ids["story_points"] == "customfield_10016"
    assert ids["epic_name"] == "customfield_10011"
    assert ids["epic_link"] == "customfield_10014"
