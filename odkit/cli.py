"""Minimal safe CLI scaffold for Open Defense Kit."""

from __future__ import annotations

import argparse

from odkit import __version__
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

    return parser


def print_doctor() -> None:
    print(BANNER)
    print("Status: scaffold ready")
    print("Root required: no")
    print("Dangerous modules enabled: no")
    print("Default mode: documentation and safety checks only")


def print_safety() -> None:
    print(BANNER)
    print("Allowed: authorized learning, owned asset review, lab testing, defensive audits.")
    print("Prohibited: phishing, credential theft, DDoS, RAT/C2, unauthorized access, spying.")
    print(f"Prohibited modules runnable: {is_allowed_risk(RiskLevel.PROHIBITED)}")


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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
