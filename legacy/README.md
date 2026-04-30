# Legacy Quarantine

This folder is the only approved place for imported legacy code from the old hacking-tool style project.

## Status

Untrusted. Do not run anything in this folder directly.

## Purpose

The legacy code is kept only so it can be reviewed, classified, and safely migrated into Open Defense Kit.

## Rules

1. Do not execute legacy files directly.
2. Do not run legacy installers.
3. Do not run scripts as root.
4. Do not preserve offensive branding in final modules.
5. Do not auto-clone or auto-install third-party offensive tools.
6. Do not migrate phishing, DDoS, RAT/C2, payload-builder, credential-theft, camera-hacking, or unauthorized exploitation modules.
7. Every migrated module must receive safety metadata, docs, and tests.

## Approved structure

```text
legacy/
├── README.md
├── original/      # raw imported code only; untrusted; do not run
├── audit/         # generated static analysis reports
└── migration-map.md
```

## Import process

When legacy code is added:

1. Put raw files under `legacy/original/`.
2. Run static analysis only.
3. Generate an audit report into `legacy/audit/`.
4. Classify every menu item and command in `legacy/migration-map.md`.
5. Remove prohibited modules.
6. Rewrite safe modules under `odkit/` instead of running legacy code.

## Decision labels

Each legacy feature must be classified as one of:

- `KEEP_SAFE`
- `REWRITE_SAFE`
- `DOCS_ONLY`
- `LAB_ONLY_DOCS`
- `REMOVE`
- `PROHIBITED`

Nothing should be promoted from `legacy/original/` until it has been reviewed.
