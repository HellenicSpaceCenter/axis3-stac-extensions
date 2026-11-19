# Changelog

Changes to the axis3hub STAC extension are recorded here. Extension versions
are independent of the reference implementation document version.

## [Unreleased]

### Added

- Define the initial `axis3hub` extension with a JSON Schema Draft 7 schema.
- Document and validate the eight existing `hub:*` fields: `hub:processId`,
  `hub:engineId`, `hub:thematicService`, `hub:license`,
  `hub:relativePath`, `hub:checksum`, `hub:workspaceName`, and `hub:layerName`.
- Support Item properties, Item and Collection assets, and Collection Item
  Asset Definitions in their existing metadata locations.
- Use processor commit `8d0bff0` (7 September 2026) as the compatibility cutoff;
  exclude the inline legend metadata introduced afterward.
- Document the intended `0.1.0` schema identifier and extension declaration.
- Add schema tests and a GitHub Actions validation workflow.

### Compatibility

- Preserve the existing `hub` prefix, field names, and metadata locations.
- Keep Hub fields optional so historical metadata can omit newer fields.
- Permit additional metadata alongside core STAC fields and other extensions.

The initial release is planned as `0.1.0`, with tag `axis3hub-v0.1.0`.
When releasing, rename this section to `0.1.0` with the actual release date
and add a new empty `Unreleased` section.
