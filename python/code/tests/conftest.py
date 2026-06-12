import pathlib

import pytest
import yaml


@pytest.fixture
def yaml_data():
    path = pathlib.Path(__file__).parent / "mocks" / "create_issues.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
