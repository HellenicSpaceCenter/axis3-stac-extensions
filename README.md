# axis3hub STAC extension

- Extension name: **axis3hub**
- Field name prefix: **hub**
- Version: **0.1.0** (independent of reference implementation document v7)
- Schema: [json-schema/schema.json](json-schema/schema.json)
- Release history: [CHANGELOG.md](CHANGELOG.md)
- Versioned identifier: `https://raw.githubusercontent.com/HellenicSpaceCenter/axis3-stac-extensions/axis3hub-v0.1.0/json-schema/schema.json`
- Scope: Item properties, Item/Collection assets, and Collection Item Asset Definitions.

The processor compatibility baseline is commit `8d0bff0` (7 September 2026).
Inline `hub:legend` and `hub:legends` are not defined at that baseline and are
excluded from this release. The separate Legends API uses the service UID in
Item keywords and returns database definitions; it requires no inline Hub legend field.

This extension standardizes existing Hub metadata without renaming keys or
changing their locations. It supplements core STAC and other extensions.

| Field | Location | Type | Meaning |
| --- | --- | --- | --- |
| hub:processId | Item properties | string | Hub process/run identifier; existing UUID and non-UUID forms remain valid. |
| hub:engineId | Item properties | string | Engine execution identifier, currently process_id_job_id. |
| hub:thematicService | Item properties | string | Thematic service name. |
| hub:license | Item properties | string | Legacy Item license metadata; does not replace Collection license. |
| hub:relativePath | Asset | string | Relative storage path. |
| hub:checksum | Asset | string | File checksum; current producer uses SHA-256 hex. |
| hub:workspaceName | Asset | string | Published vector layer's GeoServer workspace. |
| hub:layerName | Asset | string | Published vector layer identifier, including existing UUID-based names. |

All Hub fields remain optional in this compatibility schema. Stage-dependent
producer requirements are handled by the Hub operational profile. Historical
Items may omit newer fields or the extension declaration. No field is renamed
to axis3hub:*. Unknown additional metadata remains permitted; new Hub fields
must be added explicitly to this specification and schema before release.

Newly produced/enriched Items declare the versioned schema URL in
stac_extensions, appending it to existing entries. Validators retain support
for historical undeclared Items. Collection asset and item_assets support does
not introduce Item property fields at Collection top level.

## Test and release

Install `requirements-dev.txt`, then run `pytest -q`.
Tests cover all eight fields, legacy omissions, and asset scopes.

The release identifier is activated only when the reviewed commit is pushed
with tag `axis3hub-v0.1.0`. Verify that its raw JSON URL resolves and matches the
schema bytes before deploying clients that declare it. Do not move an existing
release tag; use a new version for changes. The pipelines directory mirrors
Azure DevOps to GitHub; coordinate the source commit/tag with that upstream.

Runtime components vendor this schema for offline validation. Update those
copies together and test equality with this release artifact before deployment.
