"""Acceptance coverage for the axis3hub compatibility schema."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

SCHEMA = json.loads((Path(__file__).parents[1] / "json-schema/schema.json").read_text())
VALIDATOR = Draft7Validator(SCHEMA)
ITEM = {
    "type": "Feature", "properties": {
        "hub:processId": "process-id", "hub:engineId": "process-id_job-id",
        "hub:thematicService": "security", "hub:license": "legacy-license",
    },
    "assets": {"data": {"href": "data.geojson", "hub:relativePath": "a/b/data.geojson",
        "hub:checksum": "a" * 64, "hub:workspaceName": "security",
        "hub:layerName": "existing-layer"}},
}


def test_schema_and_existing_metadata():
    Draft7Validator.check_schema(SCHEMA)
    assert SCHEMA["title"] == "axis3hub STAC extension"
    VALIDATOR.validate(ITEM)
    legacy = {"type": "Feature", "properties": {}, "assets": {}}
    VALIDATOR.validate(legacy)
    for process_id in ["550e8400-e29b-41d4-a716-446655440000", "process-id"]:
        legacy["properties"]["hub:processId"] = process_id
        VALIDATOR.validate(legacy)


@pytest.mark.parametrize("field", list(ITEM["properties"]) + list(ITEM["assets"]["data"])[1:])
def test_each_hub_field_is_explicit_and_typed(field):
    scope = "itemProperties" if field in ITEM["properties"] else "asset"
    assert field in SCHEMA["definitions"][scope]["properties"]
    bad = deepcopy(ITEM)
    target = bad["properties"] if scope == "itemProperties" else bad["assets"]["data"]
    target[field] = 42
    assert not VALIDATOR.is_valid(bad)


def test_collection_asset_scopes_and_other_extensions():
    VALIDATOR.validate({"type": "Collection", "assets": ITEM["assets"],
                        "item_assets": ITEM["assets"], "license": "CC-BY-4.0"})
    item = deepcopy(ITEM)
    item["stac_extensions"] = [SCHEMA["$id"], "https://example.org/other/schema.json"]
    item["properties"]["other:metadata"] = {"custom": True}
    VALIDATOR.validate(item)


def test_cutoff_excludes_inline_legends():
    fields = SCHEMA["definitions"]["itemProperties"]["properties"]
    assert "hub:legend" not in fields
    assert "hub:legends" not in fields
    assert "legend" not in SCHEMA["definitions"]
    assert "legendValue" not in SCHEMA["definitions"]
    assert len(fields) + len(SCHEMA["definitions"]["asset"]["properties"]) == 8
