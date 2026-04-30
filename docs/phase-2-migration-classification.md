# Phase 2: Migration Classification

Phase 2 turns the legacy quarantine area into a decision system.

The goal is not to run old code. The goal is to classify every legacy file or feature before anything is rewritten into Open Defense Kit.

## New command

```bash
odkit classify-legacy legacy/original
odkit classify-legacy legacy/original --markdown > legacy/audit/migration-classification.md
```

## Decision labels

| Label | Meaning |
|---|---|
| `KEEP_SAFE` | No risky or migration-specific patterns were found |
| `REWRITE_SAFE` | Useful defensive idea, but should be rewritten safely under `odkit/` |
| `DOCS_ONLY` | Keep as educational documentation only |
| `LAB_ONLY_DOCS` | Explain only for isolated lab learning; do not automate live-target use |
| `REMOVE` | Unsafe installer/update/destructive pattern; do not migrate |
| `PROHIBITED` | Must not be shipped or automated |

## Current classification rules

### Prohibited

The classifier marks files as `PROHIBITED` when they contain strong indicators of:

- phishing/social engineering automation
- DDoS/disruption tooling
- RAT/C2/backdoor behavior
- payload building or deployment
- camera/webcam/device spying

### Lab-only documentation

The classifier marks files as `LAB_ONLY_DOCS` when they contain indicators of:

- credential attack concepts
- exploit tooling
- SQL injection tooling
- XSS tooling
- wireless attack concepts

These topics may be explained only as controlled lab education or defensive awareness. They should not become push-button attack modules.

### Remove

The classifier marks files as `REMOVE` when they contain unsafe project plumbing such as:

- root/sudo workflows
- blind `git clone`
- remote download/script execution
- destructive delete commands
- legacy install scripts

### Rewrite safely

The classifier marks files as `REWRITE_SAFE` when they appear to describe defensive ideas such as:

- local secret scanning
- dependency auditing
- container scanning
- cloud posture review
- security headers
- defensive OSINT on owned assets

## Important limitation

This classifier is conservative static analysis. It helps triage the code, but it does not prove a file is safe. Human review is still required.

## Migration rule

No file from `legacy/original/` should be promoted directly into the production toolkit.

Approved safe ideas should be rewritten under `odkit/`, with:

- module metadata
- safety classification
- docs
- tests
- no root requirement
- no blind remote installers
- permission gates for network actions
