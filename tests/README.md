# Extension test design

Run `uv sync --locked`, then `uv run --locked pytest -q` from the repository
root. Dependencies are defined in `pyproject.toml` and resolved in `uv.lock`.
The CI workflow installs from that lockfile and runs the same tests.

## Catalogue fixture

`fixtures/SS-FR-FD-B_20261001T080122d985Z.json` is the complete catalogue Item
supplied for this review, stored as a static JSON snapshot. It includes geometry,
all properties, six existing extension declarations, links, both raster assets,
the vector asset, thumbnail, lineage asset, authentication metadata, and nested
tile/query templates. It is not a reduced projection of Hub fields. Values are
preserved; JSON whitespace is presentation only. The tests do not authenticate,
query the live catalogue, download assets, or change catalogue records.

The snapshot contains seven distinct Hub field names and 15 occurrences:
three Item properties, relative path/checksum on five assets, and workspace/layer
on the vector asset. It contains standard `license`, not legacy `hub:license`,
and neither inline legend spelling. Existing synthetic contract tests retain
coverage of the eighth field, `hub:license`, and Collection asset scopes. Inline
legends remain excluded according to processor cutoff `8d0bff0`.

## Why these tests

- Validate the full snapshot as received, without an axis3hub declaration. This
  proves that introducing this extension contract does not require rewriting
  the supplied historical Hub metadata. Explicit local schema validation does
  not require the document to declare it.
- Append the schema identifier to a copy and validate again. This demonstrates
  consumer adoption while preserving all existing declarations and metadata.
  The fixture remains unchanged; no identifiers, keys, paths, or values are
  renamed or normalized to make validation pass.
- Change each of the 15 present Hub field occurrences to a number in a fresh
  copy. Every case must raise `ValidationError`, proving that a successful
  validation is not merely the result of a permissive pass-through schema.
  Each case changes one value, so a rejection has a clear cause.

The existing `test_schema_and_existing_metadata` test already covers absent
optional Hub metadata, so the catalogue tests do not repeat that case.

Fixtures load fresh parsed JSON for each test. Mutation tests cannot contaminate
later tests. Validation reads the actual repository schema through the standard
`jsonschema.Draft7Validator` interface; there is no mocked validation result or
custom validator implementation.

## What passing proves

The snapshot is compatible with the axis3hub extension's types and locations,
and the supplied metadata can adopt its declaration without migration.

The catalogue JSON Schema tests do not validate core STAC 1.1.0 or the six
other declared extensions. This suite does not prove the release
URL is published, resolve every declared schema, inspect files, verify checksum
contents, or check GeoServer/license/authentication behavior. Existing non-Hub
metadata is retained so accidental rejection of unrelated content is caught;
this extension does not take responsibility for that content's semantics.

The local schema is used so tests are deterministic before release and do not
fail because a catalogue, identity service, network, or future release tag is
unavailable. After publication, consumers may resolve the same schema via its
versioned URL through their normal STAC validator. Public URL resolution must
be checked separately as part of release verification.

## Native PySTAC validation

`test_pystac_validation.py` additionally exercises PySTAC 1.13.0, matching the
reference processor's version. It constructs native `Item`, `Asset`, and
`Collection` objects and calls `Item.validate()` and `Collection.validate()`.
The real `JsonSchemaSTACValidator` validates both core STAC and the declared
axis3hub schema. An Item is also saved and reloaded before validation to cover
serialization. All eight Hub fields have invalid-type rejection cases that
assert PySTAC raises `STACValidationError` against the axis3hub schema. A separate
invalid core property confirms core validation also runs.

The validator's schema cache maps the canonical versioned axis3hub URL to the
repository schema. Core schemas come from PySTAC's bundled cache. No validation
methods or results are mocked, and publication is not required for these tests.

The unchanged catalogue snapshot is loaded as a PySTAC Item and checked through
`JsonSchemaSTACValidator.validate_extension()` for axis3hub specifically. Its six
other declarations are retained but not validated by this scoped check. Hrefs
are serialized without transformation so PySTAC does not resolve catalogue root
links or require catalogue authentication. This check does not claim that the
historical snapshot passes full core or unrelated extension validation.
