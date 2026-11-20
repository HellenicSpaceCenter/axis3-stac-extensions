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

This is an extension test suite, not an end-to-end deployment test. It does not
validate core STAC 1.1.0 or the six other declared extensions, prove the release
URL is published, resolve every declared schema, inspect files, verify checksum
contents, or check GeoServer/license/authentication behavior. Existing non-Hub
metadata is retained so accidental rejection of unrelated content is caught;
this extension does not take responsibility for that content's semantics.

The local schema is used so tests are deterministic before release and do not
fail because a catalogue, identity service, network, or future release tag is
unavailable. After publication, consumers may resolve the same schema via its
versioned URL through their normal STAC validator. Public URL resolution must
be checked separately as part of release verification.
