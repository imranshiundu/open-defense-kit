# Module: audit-report

| Field | Value |
| --- | --- |
| Slug | `audit-report` |
| Category | audit-reporting |
| Risk level | LOW |
| Requires authorization | No (target must still be one you own) |
| Network activity | none |
| Dependencies | none (Python standard library only) |

## What it does

Combines three local-only scanners into one graded report:

1. **Secret patterns** — API keys, AWS access keys, private-key markers in text files.
2. **Legacy risky patterns** — remote script execution, raw shell calls, destructive deletes, and references to policy-prohibited tooling.
3. **File hygiene** — world-writable files and sensitive credential filenames (`.env`, `id_rsa`, `.npmrc`, ...).

The result includes an A–F posture grade, per-severity counts, finding tables, and derived recommendations, rendered as self-contained HTML, Markdown, or JSON.

## When it is legal to use

Only against files you own or are authorized to review. The scan is read-only: the target is never executed and no data leaves the machine.

## How to use it safely

```bash
# Console summary (safe default):
odkit audit-report ./my-repo

# Full reports:
odkit audit-report ./my-repo --html report.html --json report.json --markdown report.md

# Exclude intentional fixtures (tests often contain fake secrets):
odkit audit-report ./my-repo --exclude tests,fixtures --html report.html
```

Exit codes: `0` = no findings, `1` = target missing, `2` = findings exist (CI can gate on this).

## Risks it creates

- Findings include **redacted** previews, but the preview of a matching line is still shown — review reports before sharing them.
- Static pattern scanning produces false positives (and false negatives). A finding is a signal for manual review, not proof.
- Scanning the scanner's own rule tables produces self-matches; exclude those paths when gating CI.

## How to test it in a lab

```bash
pytest tests/test_report.py -v
pytest tests/test_cli.py::TestAuditReportCommand -v

# End-to-end against a scratch directory:
mkdir -p /tmp/odk-lab && echo 'API_KEY = "abcd1234abcd1234abcd"' > /tmp/odk-lab/app.py
odkit audit-report /tmp/odk-lab --html /tmp/odk-lab-report.html
```
