"""Minimal safe CLI scaffold for Open Defense Kit."""

from __future__ import annotations

import argparse
from pathlib import Path

from odkit import __version__
from odkit.legacy_audit import audit_legacy_path, findings_to_markdown
from odkit.migration_classifier import classify_path, classifications_to_markdown
from odkit.module_registry import get_module, list_modules
from odkit.modules.local_secret_patterns import scan_path
from odkit.report import build_report, report_to_html, report_to_json, report_to_markdown
from odkit.safety import RiskLevel, is_allowed_risk, permission_statement


BANNER = "Open Defense Kit — defensive security learning and auditing"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odkit",
        description="Defense-first security learning and audit toolkit.",
    )
    parser.add_argument("--version", action="version", version=f"odkit {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("doctor", help="Check local project health.")
    subparsers.add_parser("safety", help="Print the project safety rules.")

    permission_parser = subparsers.add_parser(
        "permission",
        help="Print the permission statement for an owned target.",
    )
    permission_parser.add_argument("target", help="Owned target or lab target.")

    modules_parser = subparsers.add_parser("modules", help="List or inspect safe modules.")
    modules_subparsers = modules_parser.add_subparsers(dest="modules_command")
    modules_subparsers.add_parser("list", help="List available modules.")
    info_parser = modules_subparsers.add_parser("info", help="Show module details.")
    info_parser.add_argument("slug", help="Module slug.")

    scan_parser = subparsers.add_parser(
        "scan-secrets",
        help="Scan local files you own for common secret-like patterns.",
    )
    scan_parser.add_argument("path", help="Local file or folder to scan.")

    audit_parser = subparsers.add_parser(
        "audit-legacy",
        help="Statically audit quarantined legacy code without executing it.",
    )
    audit_parser.add_argument("path", help="Legacy file or folder to audit.")
    audit_parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print the audit report as markdown.",
    )

    classify_parser = subparsers.add_parser(
        "classify-legacy",
        help="Classify quarantined legacy code for safe migration decisions.",
    )
    classify_parser.add_argument("path", help="Legacy file or folder to classify.")
    classify_parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print the classification report as markdown.",
    )

    report_parser = subparsers.add_parser(
        "audit-report",
        help="Run the full local audit (secrets, risky patterns, file hygiene) and render a report.",
    )
    report_parser.add_argument("path", help="Local file or folder to audit (read-only, nothing is executed).")
    report_parser.add_argument(
        "--exclude",
        dest="exclude",
        default="",
        metavar="PARTS",
        help="Comma-separated path parts whose findings are dropped (e.g. tests,fixtures).",
    )
    report_parser.add_argument("--html", dest="html", metavar="FILE", help="Write a self-contained HTML report.")
    report_parser.add_argument("--json", dest="json", metavar="FILE", help="Write the report as JSON.")
    report_parser.add_argument(
        "--markdown", dest="markdown", metavar="FILE", help="Write the report as markdown."
    )
    report_parser.add_argument(
        "--stdout", dest="stdout", choices=("html", "json", "markdown"), help="Print the report to stdout instead of a file."
    )

    return parser


def print_doctor() -> None:
    print(BANNER)
    print("Status: scaffold ready")
    print("Root required: no")
    print("Dangerous modules enabled: no")
    print("Default mode: local-only documentation and safety checks")


def print_safety() -> None:
    print(BANNER)
    print("Allowed: authorized learning, owned asset review, lab testing, defensive audits.")
    print("Prohibited: phishing, credential theft, DDoS, RAT/C2, unauthorized access, spying.")
    print(f"Prohibited modules runnable: {is_allowed_risk(RiskLevel.PROHIBITED)}")


def print_modules() -> None:
    for module in list_modules():
        status = "enabled" if module.enabled else "disabled"
        print(f"{module.slug}\t{module.safety.risk.value}\t{status}\t{module.safety.name}")


def print_module_info(slug: str) -> int:
    module = get_module(slug)
    if module is None:
        print(f"Unknown module: {slug}")
        return 1

    safety = module.safety
    print(safety.name)
    print(f"Slug: {module.slug}")
    print(f"Category: {safety.category}")
    print(f"Risk: {safety.risk.value}")
    print(f"Requires authorization: {safety.requires_authorization}")
    print(f"Network activity: {safety.network_activity}")
    print(f"Docs: {module.docs}")
    print(f"Description: {safety.description}")
    return 0


def run_secret_scan(raw_path: str) -> int:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    findings = scan_path(path)
    if not findings:
        print("No common secret-like patterns found.")
        return 0

    print(f"Found {len(findings)} possible secret-like pattern(s). Review manually.")
    for finding in findings:
        print(f"{finding.path}:{finding.line}\t{finding.pattern}\t{finding.preview}")
    return 2


def run_legacy_audit(raw_path: str, markdown: bool) -> int:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    findings = audit_legacy_path(path)
    if markdown:
        print(findings_to_markdown(findings))
        return 0 if not findings else 2

    if not findings:
        print("No risky legacy patterns found by the basic static scanner.")
        return 0

    print(f"Found {len(findings)} risky legacy pattern(s).")
    for finding in findings:
        print(
            f"{finding.path}:{finding.line}\t{finding.category}\t"
            f"{finding.description}\t{finding.preview}"
        )
    return 2


def run_legacy_classification(raw_path: str, markdown: bool) -> int:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    results = classify_path(path)
    if markdown:
        print(classifications_to_markdown(results))
        return 0

    if not results:
        print("No text files were found to classify.")
        return 0

    for result in results:
        tokens = ", ".join(result.matched_tokens) or "none"
        print(f"{result.path}\t{result.decision.value}\t{result.reason}\t{tokens}")
    return 0


def run_audit_report(args) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    try:
        excluded_parts = {part.strip() for part in (args.exclude or "").split(",") if part.strip()}
        report = build_report(str(path), exclude=excluded_parts)
    except FileNotFoundError as error:
        print(error)
        return 1

    renderers = {
        "html": report_to_html,
        "json": report_to_json,
        "markdown": report_to_markdown,
    }
    outputs = {
        "html": args.html,
        "json": args.json,
        "markdown": args.markdown,
    }

    for fmt, out_path in outputs.items():
        if not out_path:
            continue
        target_path = Path(out_path).expanduser()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(renderers[fmt](report), encoding="utf-8")
        print(f"Wrote {fmt} report to {target_path}")

    if args.stdout:
        print(renderers[args.stdout](report))
    elif not any(outputs.values()):
        # Default: short console summary so the command is useful without flags.
        counts = report.severity_counts
        print(f"ODK audit report {report.scan_id} for {report.target}")
        print(f"Grade: {report.grade}  |  files scanned: {report.files_scanned}  |  findings: {report.total_findings}")
        print(
            f"CRITICAL: {counts['CRITICAL']}  HIGH: {counts['HIGH']}  MEDIUM: {counts['MEDIUM']}  LOW: {counts['LOW']}"
        )
        print("Pass --html/--json/--markdown to render a full report.")

    return 0 if report.total_findings == 0 else 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        print_doctor()
        return 0

    if args.command == "safety":
        print_safety()
        return 0

    if args.command == "permission":
        print(permission_statement(args.target))
        return 0

    if args.command == "modules":
        if args.modules_command == "list":
            print_modules()
            return 0
        if args.modules_command == "info":
            return print_module_info(args.slug)

    if args.command == "scan-secrets":
        return run_secret_scan(args.path)

    if args.command == "audit-legacy":
        return run_legacy_audit(args.path, args.markdown)

    if args.command == "classify-legacy":
        return run_legacy_classification(args.path, args.markdown)

    if args.command == "audit-report":
        return run_audit_report(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
