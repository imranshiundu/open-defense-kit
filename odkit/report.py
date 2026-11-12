"""Security audit report generator for Open Defense Kit.

This module combines the local-only defensive scanners (secret patterns,
legacy risk audit, file hygiene) into a single professional report that can
be rendered as HTML, Markdown, or JSON.

Everything is static and local: the target is only read, never executed, and
no finding is ever sent anywhere.
"""

from __future__ import annotations

import html
import json
import platform
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from odkit.legacy_audit import LegacyFinding, audit_legacy_path
from odkit.modules.local_secret_patterns import Finding, scan_path

CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"

SEVERITY_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3}
SEVERITY_WEIGHT = {CRITICAL: 10, HIGH: 5, MEDIUM: 2, LOW: 1}

SECRET_SEVERITY = {
    "private_key_marker": CRITICAL,
    "aws_access_key_like": CRITICAL,
    "generic_api_key": HIGH,
}

LEGACY_SEVERITY = {
    "phishing": HIGH,
    "ddos": HIGH,
    "rat_c2": HIGH,
    "payload": HIGH,
    "credential_attack": HIGH,
    "camera_hacking": HIGH,
    "remote_script": MEDIUM,
    "raw_shell": MEDIUM,
    "destructive_delete": MEDIUM,
    "root_or_privilege": MEDIUM,
    "blind_clone": LOW,
}

CREDENTIAL_FILENAMES = {".env", ".npmrc", ".netrc", "id_rsa", "credentials", ".git-credentials"}


@dataclass(frozen=True)
class HygieneFinding:
    """A file-hygiene finding (permissions or sensitive filenames)."""

    path: str
    kind: str
    severity: str
    detail: str


@dataclass
class AuditReport:
    """Full result of one audit run."""

    target: str
    scan_id: str
    generated_at: str
    files_scanned: int
    secret_findings: list[Finding]
    legacy_findings: list[LegacyFinding]
    hygiene_findings: list[HygieneFinding]
    severity_counts: dict[str, int] = field(default_factory=dict)
    grade: str = "A"

    @property
    def total_findings(self) -> int:
        return len(self.secret_findings) + len(self.legacy_findings) + len(self.hygiene_findings)


def _grade_for(severity_counts: dict[str, int]) -> str:
    """Map weighted severity counts to a letter grade."""

    score = sum(SEVERITY_WEIGHT.get(sev, 1) * count for sev, count in severity_counts.items())
    if score == 0:
        return "A"
    if score <= 5:
        return "B"
    if score <= 15:
        return "C"
    if score <= 40:
        return "D"
    return "F"


def _scan_hygiene(root: Path, skip_dirs: set[str]) -> list[HygieneFinding]:
    """Check file permissions and sensitive filenames without reading contents."""

    findings: list[HygieneFinding] = []
    candidates = [root] if root.is_file() else root.rglob("*")

    for path in candidates:
        if root.is_dir() and any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue

        name = path.name.lower()
        if name in CREDENTIAL_FILENAMES:
            findings.append(
                HygieneFinding(
                    path=str(path),
                    kind="credential_file_present",
                    severity=HIGH if name in {".env", "id_rsa"} else MEDIUM,
                    detail="Sensitive credential file present in the tree. Ensure it is git-ignored and never committed.",
                )
            )

        try:
            mode = path.stat().st_mode & 0o777
        except OSError:
            continue
        # World-writable = "others" have the write bit.
        if mode & 0o002:
            findings.append(
                HygieneFinding(
                    path=str(path),
                    kind="world_writable_file",
                    severity=MEDIUM,
                    detail=f"File mode {oct(mode)} is writable by users other than the owner.",
                )
            )

    return findings


def _filter_excluded(entries: list, exclude: set[str]) -> list:
    """Drop findings whose path contains an excluded path part.

    Exclusions are useful for CI runs: test fixtures intentionally contain
    fake secrets, so `--exclude tests` keeps the gate focused on real code.
    """

    if not exclude:
        return entries
    return [e for e in entries if not (set(Path(e.path).parts) & exclude)]


def build_report(target: str, exclude: set[str] | None = None) -> AuditReport:
    """Run every local defensive scan against a target path.

    `exclude` is a set of path-part names (e.g. {"tests", "fixtures"}) whose
    findings are dropped from the report. Scanning remains read-only.
    """

    root = Path(target).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"target not found: {root}")

    from odkit.modules.local_secret_patterns import SKIP_DIRS

    exclude = exclude or set()
    secret_findings = _filter_excluded(scan_path(root), exclude)
    legacy_findings = _filter_excluded(audit_legacy_path(root), exclude)
    hygiene_findings = _filter_excluded(_scan_hygiene(root, SKIP_DIRS), exclude)

    # Bound hygiene noise: credential files are already covered by the secret
    # scanner when they contain secrets; here we only report their presence.
    all_files = [p for p in ([root] if root.is_file() else root.rglob("*")) if p.is_file()]
    kept_files = [p for p in all_files if not (set(p.parts) & exclude)]
    files_scanned = len(kept_files)

    severity_counts: dict[str, int] = {CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0}
    for finding in secret_findings:
        severity_counts[SECRET_SEVERITY.get(finding.pattern, MEDIUM)] += 1
    for finding in legacy_findings:
        severity_counts[LEGACY_SEVERITY.get(finding.category, MEDIUM)] += 1
    for finding in hygiene_findings:
        severity_counts[finding.severity] += 1

    return AuditReport(
        target=str(root),
        scan_id=secrets.token_hex(4),
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        files_scanned=files_scanned,
        secret_findings=secret_findings,
        legacy_findings=legacy_findings,
        hygiene_findings=hygiene_findings,
        severity_counts=severity_counts,
        grade=_grade_for(severity_counts),
    )


def _recommendations(report: AuditReport) -> list[str]:
    """Derive human recommendations from the findings."""

    recs: list[str] = []
    if report.severity_counts[CRITICAL]:
        recs.append("Revoke and rotate every exposed key or private key immediately; assume committed secrets are compromised.")
    if any(f.pattern == "generic_api_key" for f in report.secret_findings):
        recs.append("Move API keys into environment variables or a secret manager; add .env to .gitignore.")
    if report.legacy_findings:
        recs.append("Run `odkit classify-legacy` on the risky files and apply the suggested migration decisions.")
    if any(f.kind == "credential_file_present" for f in report.hygiene_findings):
        recs.append("Credential files found in the tree: verify they are git-ignored and excluded from builds.")
    if any(f.kind == "world_writable_file" for f in report.hygiene_findings):
        recs.append("Restrict permissions on world-writable files (chmod o-w).")
    if not recs:
        recs.append("No action items from this scan. Keep static checks in CI to stay clean.")
    return recs


def report_to_json(report: AuditReport) -> str:
    """Render the report as JSON."""

    payload = {
        "tool": "open-defense-kit",
        "module": "audit-report",
        "scan_id": report.scan_id,
        "generated_at": report.generated_at,
        "target": report.target,
        "files_scanned": report.files_scanned,
        "total_findings": report.total_findings,
        "severity_counts": report.severity_counts,
        "grade": report.grade,
        "secrets": [
            {"path": f.path, "line": f.line, "pattern": f.pattern, "severity": SECRET_SEVERITY.get(f.pattern, MEDIUM), "preview": f.preview}
            for f in report.secret_findings
        ],
        "legacy_risks": [
            {"path": f.path, "line": f.line, "category": f.category, "severity": LEGACY_SEVERITY.get(f.category, MEDIUM), "description": f.description, "preview": f.preview}
            for f in report.legacy_findings
        ],
        "hygiene": [
            {"path": f.path, "kind": f.kind, "severity": f.severity, "detail": f.detail}
            for f in report.hygiene_findings
        ],
        "recommendations": _recommendations(report),
        "disclaimer": "Static, local-only pattern review. It does not prove code is safe or unsafe by itself.",
    }
    return json.dumps(payload, indent=2)


def report_to_markdown(report: AuditReport) -> str:
    """Render the report as Markdown."""

    out = [
        f"# ODK Security Audit Report — `{report.target}`",
        "",
        f"Scan ID: `{report.scan_id}`  |  Generated: {report.generated_at}  |  Files scanned: {report.files_scanned}",
        "",
        f"**Grade: {report.grade}** — "
        + ", ".join(f"{sev}: {count}" for sev, count in report.severity_counts.items())
        + f" — total: {report.total_findings}",
        "",
    ]
    if report.secret_findings:
        out += ["## Secrets", "", "| File | Line | Pattern | Severity | Preview |", "|---|---:|---|---|---|"]
        for f in report.secret_findings:
            preview = f.preview.replace("|", "\\|")
            out.append(f"| `{f.path}` | {f.line} | `{f.pattern}` | {SECRET_SEVERITY.get(f.pattern, MEDIUM)} | `{preview}` |")
        out.append("")
    if report.legacy_findings:
        out += ["## Legacy / risky patterns", "", "| File | Line | Category | Severity | Description |", "|---|---:|---|---|---|"]
        for f in report.legacy_findings:
            out.append(f"| `{f.path}` | {f.line} | `{f.category}` | {LEGACY_SEVERITY.get(f.category, MEDIUM)} | {f.description} |")
        out.append("")
    if report.hygiene_findings:
        out += ["## File hygiene", "", "| File | Kind | Severity | Detail |", "|---|---|---|---|"]
        for f in report.hygiene_findings:
            out.append(f"| `{f.path}` | `{f.kind}` | {f.severity} | {f.detail} |")
        out.append("")
    if report.total_findings == 0:
        out += ["No findings from the local static scans.", ""]
    out += ["## Recommendations", ""]
    out += [f"- {rec}" for rec in _recommendations(report)]
    out += ["", "> Static, local-only pattern review. It does not prove code is safe or unsafe by itself."]
    return "\n".join(out)


_SEVERITY_COLORS = {
    CRITICAL: "#ff4d6d",
    HIGH: "#ff9f43",
    MEDIUM: "#f5d76e",
    LOW: "#78c4d4",
}


def report_to_html(report: AuditReport) -> str:
    """Render the report as a self-contained dark-themed HTML page."""

    def esc(text: str) -> str:
        return html.escape(str(text))

    def badge(sev: str) -> str:
        color = _SEVERITY_COLORS.get(sev, "#888")
        return f'<span style="background:{color}22;color:{color};border:1px solid {color}55;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600">{esc(sev)}</span>'

    def rows(entries, render) -> str:
        if not entries:
            return '<tr><td colspan="5" style="color:#7a869a;font-style:italic">No findings in this section.</td></tr>'
        return "".join(render(e) for e in entries)

    secret_rows = rows(
        report.secret_findings,
        lambda f: (
            "<tr>"
            f'<td class="mono">{esc(f.path)}</td><td>{f.line}</td>'
            f"<td><code>{esc(f.pattern)}</code></td><td>{badge(SECRET_SEVERITY.get(f.pattern, MEDIUM))}</td>"
            f'<td class="mono dim">{esc(f.preview)}</td>'
            "</tr>"
        ),
    )
    legacy_rows = rows(
        report.legacy_findings,
        lambda f: (
            "<tr>"
            f'<td class="mono">{esc(f.path)}</td><td>{f.line}</td>'
            f"<td><code>{esc(f.category)}</code></td><td>{badge(LEGACY_SEVERITY.get(f.category, MEDIUM))}</td>"
            f'<td class="dim">{esc(f.description)}</td>'
            "</tr>"
        ),
    )
    hygiene_rows = rows(
        report.hygiene_findings,
        lambda f: (
            "<tr>"
            f'<td class="mono">{esc(f.path)}</td>'
            f"<td><code>{esc(f.kind)}</code></td><td>{badge(f.severity)}</td>"
            f'<td class="dim">{esc(f.detail)}</td><td></td>'
            "</tr>"
        ),
    )

    rec_items = "".join(f"<li>{esc(r)}</li>" for r in _recommendations(report))
    sev_cards = "".join(
        f'<div class="card"><div class="sev" style="color:{_SEVERITY_COLORS[sev]}">{count}</div><div class="lbl">{sev}</div></div>'
        for sev, count in report.severity_counts.items()
    )

    grade_color = {"A": "#3dbb78", "B": "#8bc34a", "C": "#f5d76e", "D": "#ff9f43", "F": "#ff4d6d"}[report.grade]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ODK Security Audit — {esc(Path(report.target).name)}</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:#0e1111; color:#e6e9ee; font:14px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 40px 24px 64px; }}
  header.top {{ border-left:4px solid #ff6a00; padding-left:16px; margin-bottom:28px; }}
  h1 {{ margin:0 0 4px; font-size:24px; letter-spacing:.4px; }}
  .brand {{ color:#ff6a00; font-weight:700; }}
  .meta {{ color:#7a869a; font-size:12.5px; }}
  .summary {{ display:flex; gap:12px; flex-wrap:wrap; align-items:stretch; margin:18px 0 30px; }}
  .grade-card {{ background:#171b1d; border:1px solid #262c2f; border-radius:12px; padding:14px 22px; text-align:center; min-width:110px; }}
  .grade {{ font-size:40px; font-weight:800; line-height:1; }}
  .card {{ background:#171b1d; border:1px solid #262c2f; border-radius:12px; padding:10px 18px; text-align:center; min-width:96px; }}
  .sev {{ font-size:24px; font-weight:700; line-height:1.2; }}
  .lbl {{ color:#7a869a; font-size:11px; letter-spacing:1px; }}
  section {{ margin-bottom:34px; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:1.4px; color:#c9d1dc; border-bottom:1px solid #262c2f; padding-bottom:8px; }}
  table {{ width:100%; border-collapse:collapse; background:#121516; border:1px solid #262c2f; border-radius:8px; overflow:hidden; }}
  th {{ background:#171b1d; color:#9aa5b1; text-align:left; font-size:11px; letter-spacing:.8px; text-transform:uppercase; padding:9px 12px; }}
  td {{ padding:8px 12px; border-top:1px solid #1f2427; vertical-align:top; word-break:break-word; }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12.5px; }}
  .dim {{ color:#8b95a3; }}
  code {{ color:#e8b36a; }}
  ul.recs {{ margin:0; padding-left:20px; }}
  ul.recs li {{ margin-bottom:8px; }}
  footer {{ color:#5f6b7a; font-size:11.5px; border-top:1px solid #262c2f; padding-top:14px; margin-top:10px; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1><span class="brand">Open Defense Kit</span> — Security Audit Report</h1>
    <div class="meta">Target: <code>{esc(report.target)}</code> &nbsp;|&nbsp; Scan ID: <code>{esc(report.scan_id)}</code> &nbsp;|&nbsp; {esc(report.generated_at)} &nbsp;|&nbsp; Files scanned: {report.files_scanned} &nbsp;|&nbsp; Host: {esc(platform.system())}</div>
  </header>

  <div class="summary">
    <div class="grade-card"><div class="grade" style="color:{grade_color}">{report.grade}</div><div class="lbl">POSTURE GRADE</div></div>
    {sev_cards}
    <div class="card"><div class="sev">{report.total_findings}</div><div class="lbl">TOTAL FINDINGS</div></div>
  </div>

  <section>
    <h2>Exposed secrets</h2>
    <table>
      <tr><th>File</th><th>Line</th><th>Pattern</th><th>Severity</th><th>Preview</th></tr>
      {secret_rows}
    </table>
  </section>

  <section>
    <h2>Legacy / risky patterns</h2>
    <table>
      <tr><th>File</th><th>Line</th><th>Category</th><th>Severity</th><th>Description</th></tr>
      {legacy_rows}
    </table>
  </section>

  <section>
    <h2>File hygiene</h2>
    <table>
      <tr><th>File</th><th>Kind</th><th>Severity</th><th>Detail</th><th></th></tr>
      {hygiene_rows}
    </table>
  </section>

  <section>
    <h2>Recommendations</h2>
    <ul class="recs">{rec_items}</ul>
  </section>

  <footer>
    Open Defense Kit · audit-report module · static, local-only pattern review. Nothing was executed and nothing left this machine.
    This report does not prove code is safe or unsafe by itself — review every finding manually.
  </footer>
</div>
</body>
</html>
"""
