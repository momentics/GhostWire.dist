# ABI Policy

## Versioning

GhostWire distribution artifacts follow semantic versioning:

- major: incompatible ABI or packaging changes
- minor: backward-compatible additions
- patch: fixes without intended ABI breakage

## Consumer Guidance

- Pin an explicit release tag such as `v1.2.3`
- Verify downloaded artifacts with the published SHA-256 file
- Treat a major version bump as requiring compatibility review

## Artifact Contract

Each published release is expected to include:

- one or more platform archives
- one headers archive
- `manifest.json`
- a SHA-256 checksum file
