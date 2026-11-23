"""Consumer-facing regression tests using the supplied catalogue Item."""

from copy import deepcopy

import pytest
from jsonschema import ValidationError

ASSET_KEYS = (
    "Flood_Depth_20261001T080122d985Z",
    "Flood_Extent_20261001T080122d985Z",
    "Flooded_Areas_20261001T080122d985Z",
    "thumbnail",
    "lineage",
)
VECTOR_KEY = "Flooded_Areas_20261001T080122d985Z"
HUB_FIELD_PATHS = [
    ("properties", field)
    for field in ("hub:processId", "hub:engineId", "hub:thematicService")
] + [
    ("assets", asset_key, field)
    for asset_key in ASSET_KEYS
    for field in ("hub:relativePath", "hub:checksum")
] + [
    ("assets", VECTOR_KEY, "hub:workspaceName"),
    ("assets", VECTOR_KEY, "hub:layerName"),
]


def test_existing_catalogue_item_validates_without_changes(
    catalogue_item, extension_schema, extension_validator
):
    """The full historical representation is compatible without a declaration."""
    assert catalogue_item["id"] == "SS-FR-FD-B_20261001T080122d985Z"
    assert catalogue_item["stac_version"] == "1.1.0"
    assert set(catalogue_item["assets"]) == set(ASSET_KEYS)
    assert extension_schema["$id"] not in catalogue_item["stac_extensions"]
    assert "hub:license" not in catalogue_item["properties"]
    assert catalogue_item["properties"]["license"] == "GNSSP-NCVAL"
    assert "hub:legend" not in catalogue_item["properties"]
    assert "hub:legends" not in catalogue_item["properties"]

    extension_validator.validate(catalogue_item)


def test_catalogue_item_can_adopt_the_extension_without_metadata_migration(
    catalogue_item, extension_schema, extension_validator
):
    """A consumer appends one URL; all existing content stays in place."""
    original = deepcopy(catalogue_item)
    declared_item = deepcopy(catalogue_item)
    declared_item["stac_extensions"].append(extension_schema["$id"])

    extension_validator.validate(declared_item)

    assert declared_item["stac_extensions"][:-1] == original["stac_extensions"]
    assert declared_item["stac_extensions"][-1] == extension_schema["$id"]
    assert {key: value for key, value in declared_item.items() if key != "stac_extensions"} == {
        key: value for key, value in original.items() if key != "stac_extensions"
    }
    assert catalogue_item == original


@pytest.mark.parametrize("field_path", HUB_FIELD_PATHS, ids=lambda path: "/".join(path))
def test_wrong_hub_field_type_is_rejected_in_catalogue_item(
    catalogue_item, extension_schema, extension_validator, field_path
):
    """A valid real Item must fail if one present Hub string becomes a number."""
    catalogue_item["stac_extensions"].append(extension_schema["$id"])
    target = catalogue_item
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = 42

    with pytest.raises(ValidationError):
        extension_validator.validate(catalogue_item)
