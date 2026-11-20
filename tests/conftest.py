"""Load the extension schema and a fresh catalogue snapshot for each test."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def extension_schema():
    schema = json.loads((ROOT / "json-schema/schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return schema


@pytest.fixture
def extension_validator(extension_schema):
    return Draft7Validator(extension_schema)


@pytest.fixture
def catalogue_item():
    path = ROOT / "tests/fixtures/SS-FR-FD-B_20261001T080122d985Z.json"
    return json.loads(path.read_text(encoding="utf-8"))
