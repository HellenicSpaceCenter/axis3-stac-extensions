# axis3hub STAC extension

The **axis3hub** extension defines existing custom Hub metadata using the
**hub** field prefix. Field names, values, and metadata locations stay unchanged.
It supplements core STAC and other declared extensions.

- Version: **0.1.0**
- [JSON Schema](json-schema/schema.json)
- [Changelog](CHANGELOG.md)
- Scope: Item properties, Item/Collection assets, and Collection Item Asset Definitions.

## Fields

| Field | Location | Type | Meaning |
| --- | --- | --- | --- |
| `hub:processId` | Item properties | string | Hub process/run identifier; UUID and non-UUID forms are supported. |
| `hub:engineId` | Item properties | string | Engine execution identifier. |
| `hub:thematicService` | Item properties | string | Thematic service name. |
| `hub:license` | Item properties | string | Legacy Item license metadata; does not replace standard `license`. |
| `hub:relativePath` | Asset | string | Relative storage path. |
| `hub:checksum` | Asset | string | File checksum; the current producer uses SHA-256 hex. |
| `hub:workspaceName` | Asset | string | GeoServer workspace for a published vector layer. |
| `hub:layerName` | Asset | string | Published vector layer identifier. |

All eight fields are optional for compatibility with historical metadata. Their
types are checked when present. Other metadata remains permitted. Inline
`hub:legend` and `hub:legends` are not defined by this version.

## Declare the extension

Append this schema URL to the Item's top-level `stac_extensions` array, keeping
all existing entries:

```text
https://raw.githubusercontent.com/HellenicSpaceCenter/axis3-stac-extensions/axis3hub-v0.1.0/json-schema/schema.json
```

For example, this is an Item fragment, not a complete STAC Item:

```json
{
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
    "https://raw.githubusercontent.com/HellenicSpaceCenter/axis3-stac-extensions/axis3hub-v0.1.0/json-schema/schema.json"
  ],
  "properties": {
    "hub:processId": "process-123",
    "hub:thematicService": "security"
  }
}
```

The URL identifies the `json-schema/schema.json` file at release tag
`axis3hub-v0.1.0`. That tag and file must be published and accessible before
consumers can resolve the URL. Do not substitute the repository's HTML homepage.
There is one extension declaration for all its fields, not one per field or asset.
Existing undeclared Items can be checked directly against the schema without
renaming fields or adding optional metadata.

## Validate an Item locally

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed,
run this from the repository root to create the local `.venv` and install the
validation and test dependencies from the committed lockfile:

```bash
uv sync --locked
```

Save the following as `validate_item.py` and run it with
`uv run --locked python validate_item.py`. Use the supplied full catalogue
example, or replace `item_path` with your own Item file:

```python
import json
from pathlib import Path

from jsonschema import Draft7Validator

schema = json.loads(Path("json-schema/schema.json").read_text(encoding="utf-8"))
item_path = Path("tests/fixtures/SS-FR-FD-B_20261001T080122d985Z.json")
item = json.loads(item_path.read_text(encoding="utf-8"))

Draft7Validator.check_schema(schema)
validator = Draft7Validator(schema)
validator.validate(item)  # Raises ValidationError if Hub metadata is invalid.
print("Item is compatible with the axis3hub schema")

# To adopt the extension, preserve the existing declarations and append its URL.
extensions = item.setdefault("stac_extensions", [])
if schema["$id"] not in extensions:
    extensions.append(schema["$id"])
validator.validate(item)
print("Item with the axis3hub declaration also validates")
```

The example works locally before publication because it reads the schema file.
Appending the URL alone does not download or apply a schema: the validator above
explicitly applies the local one. After publication, a STAC validator that resolves
`stac_extensions` can retrieve the schema through its URL.

This check validates only axis3hub's constraints. Continue validating against
core STAC and the other extensions separately. It does not download assets,
verify checksums against file contents, resolve GeoServer layers, or validate
licenses and authentication. No changes to Hub validators or Stageout are
required to use the declared extension through their existing STAC flow.

## Validate with PySTAC

The development dependencies include `pystac[validation]`. For a native STAC Item
before schema publication, use PySTAC's validator with the candidate schema in
its cache:

```python
import json
from pathlib import Path

import pystac
from pystac.validation import JsonSchemaSTACValidator

schema = json.loads(Path("json-schema/schema.json").read_text(encoding="utf-8"))
item = pystac.Item.from_file("your-item.json")
if schema["$id"] not in item.stac_extensions:
    item.stac_extensions.append(schema["$id"])
validator = JsonSchemaSTACValidator()
validator.schema_cache[schema["$id"]] = schema
item.validate(validator=validator)
```

This validates core STAC and every declared extension, raising
`pystac.STACValidationError` for invalid metadata. Other declared extensions may
require network access. After the release URL is published, `item.validate()`
can resolve axis3hub normally without the local cache entry.

## Run the tests

```bash
uv run --locked pytest -q
```

Tests validate the full catalogue example, its adoption of the declaration, and
incorrect Hub field types. See [test design and fixture provenance](tests/README.md)
for coverage and limitations.

Dependencies and pytest settings are defined in `pyproject.toml`; `uv.lock`
records the resolved versions used locally and in CI. This is a schema project,
not an installable Python package, so uv manages its environment without
building or publishing a Python distribution.
