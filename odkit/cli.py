"""Minimal safe CLI scaffold for Open Defense Kit."""

from __future__ import annotations

import argparse
from pathlib import Path

from odkit import __version__
from odkit.legacy_audit import audit_legacy_path, findings_to_markdown
from odkit.module_registry import get_module, list_modules
from odkit.modules.local_secret_patterns import scan_path
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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
