"""PySTAC native validators tests with the repository extension schema."""

from datetime import datetime, timezone

import pystac
import pytest
from pystac.validation import JsonSchemaSTACValidator


@pytest.fixture
def native_validator(extension_schema):
    validator = JsonSchemaSTACValidator()
    # Resolve the real declaration to the candidate schema before publication.
    # Keep PySTAC's bundled core schemas and its validation implementation intact.
    validator.schema_cache[extension_schema["$id"]] = extension_schema
    return validator


@pytest.fixture
def native_item(extension_schema):
    item = pystac.Item(
        id="native-item",
        geometry=None,
        bbox=None,
        datetime=datetime(2026, 1, 1, tzinfo=timezone.utc),
        properties={
            "hub:processId": "process-id",
            "hub:engineId": "process-id_job-id",
            "hub:thematicService": "security",
            "hub:license": "legacy-license",
        },
        stac_extensions=[extension_schema["$id"]],
    )
    item.add_asset("data", pystac.Asset(
        href="https://example.org/data.geojson",
        media_type="application/geo+json",
        extra_fields={
            "hub:relativePath": "collection/item/data.geojson",
            "hub:checksum": "a" * 64,
            "hub:workspaceName": "security",
            "hub:layerName": "existing-layer",
        },
    ))
    return item


def test_native_item_roundtrip_validates_core_and_extension(
    native_item, native_validator, extension_schema, tmp_path
):
    path = tmp_path / "item.json"
    native_item.save_object(dest_href=str(path))
    restored = pystac.Item.from_file(str(path))

    schemas = restored.validate(validator=native_validator)

    assert extension_schema["$id"] in schemas
    assert len(schemas) == 2  # Core STAC and axis3hub both ran.
    assert restored.properties == native_item.properties
    assert restored.assets["data"].to_dict() == native_item.assets["data"].to_dict()


@pytest.mark.parametrize("scope,field", [
    ("item", "hub:processId"),
    ("item", "hub:engineId"),
    ("item", "hub:thematicService"),
    ("item", "hub:license"),
    ("asset", "hub:relativePath"),
    ("asset", "hub:checksum"),
    ("asset", "hub:workspaceName"),
    ("asset", "hub:layerName"),
])
def test_native_item_rejects_invalid_hub_type(
    native_item, native_validator, extension_schema, scope, field
):
    target = (native_item.properties if scope == "item"
              else native_item.assets["data"].extra_fields)
    target[field] = 42

    with pytest.raises(pystac.STACValidationError) as error:
        native_item.validate(validator=native_validator)
    assert extension_schema["$id"] in str(error.value)


def test_native_validation_also_rejects_invalid_core_metadata(
    native_item, native_validator
):
    native_item.properties["title"] = 42
    with pytest.raises(pystac.STACValidationError):
        native_item.validate(validator=native_validator)


def test_native_collection_validates_core_and_extension(
    native_item, native_validator, extension_schema
):
    collection = pystac.Collection(
        id="native-collection",
        description="Native collection validation",
        extent=pystac.Extent(
            pystac.SpatialExtent([[-180, -90, 180, 90]]),
            pystac.TemporalExtent([[datetime(2026, 1, 1, tzinfo=timezone.utc), None]]),
        ),
        license="proprietary",
        stac_extensions=[extension_schema["$id"]],
    )
    collection.add_asset("data", native_item.assets["data"].clone())
    schemas = collection.validate(validator=native_validator)
    assert extension_schema["$id"] in schemas
    assert len(schemas) == 2


def test_catalogue_item_extension_validates_through_pystac(
    catalogue_item, native_validator, extension_schema
):
    item = pystac.Item.from_dict(catalogue_item)
    item.stac_extensions.append(extension_schema["$id"])
    # The historical fixture declares six unrelated extensions. Validate only
    # axis3hub here without changing those declarations or fetching their schemas.
    result = native_validator.validate_extension(
        item.to_dict(transform_hrefs=False), pystac.STACObjectType.ITEM,
        catalogue_item["stac_version"], extension_schema["$id"],
    )
    assert result == extension_schema["$id"]
