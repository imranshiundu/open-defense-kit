# Open Defense Kit

Open Defense Kit is an ethical, legal, defense-first security toolkit project. It is being built as a safer replacement and rebrand for unsafe all-in-one hacking-tool launchers.

The goal is not to package offensive tools blindly. The goal is to create a controlled security learning and audit environment where every module is documented, permission-based, and safe by default.

## Mission

Build a defensive cybersecurity toolkit for:

- authorized security education
- blue-team learning
- lab-based vulnerability research
- defensive audits
- OSINT and recon on owned assets
- cloud, container, mobile, and code security checks
- security awareness and safe tooling discovery

## Non-negotiable rule

Use this project only on systems, accounts, networks, repositories, domains, and applications you own or have explicit written permission to test.

Open Defense Kit will not be designed as a phishing kit, malware kit, botnet tool, DDoS tool, credential theft tool, RAT builder, or unauthorized exploitation framework.

## Why this exists

The original `hackingtools` style of project has serious failures:

- unsafe root-first installation
- blind cloning of third-party offensive repositories
- poor dependency hygiene
- broken commands and fragile menus
- no trust model
- no signed releases or checksums
- no safety boundaries
- no authorization workflow
- no distinction between defensive, lab-only, and dangerous tools

Open Defense Kit turns those failures into design rules.

## Current status

This repository currently contains the diagnosis, documentation, safety policy, roadmap, and safe project scaffold. The original code should be added later only after rebranding, pruning, and safety refactoring.

## Repository structure

```text
.
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   ├── diagnosis.md
│   ├── use-cases.md
│   ├── improvement-plan.md
│   ├── safety-model.md
│   └── rebrand-plan.md
└── odkit/
    ├── __init__.py
    └── safety.py
```

## Safe-first design principles

1. No root-first installer.
2. No blind `git clone` execution.
3. No dangerous modules enabled by default.
4. No hidden network activity.
5. No credential harvesting.
6. No phishing automation.
7. No DDoS tooling.
8. No RAT/C2/payload builder modules.
9. Every module must declare category, risk level, permissions required, and safe usage.
10. Lab-only tools must be clearly marked and gated.

## Planned safe module categories

- Asset inventory
- Code secret scanning
- Dependency auditing
- Container image scanning
- Cloud configuration review
- Web header/security posture checks
- Log review helpers
- Forensics learning tools
- Reverse engineering lab references
- Mobile app security lab setup
- Defensive OSINT for owned domains

## Not planned

The following categories should be removed or permanently disabled unless they are converted into harmless educational notes:

- DDoS tools
- phishing kits
- RATs/C2 frameworks
- payload builders
- credential cracking against real accounts
- webcam/camera hacking tools
- wireless deauth/evil-twin tooling outside isolated labs
- automated exploitation against third-party targets

## Quick start for developers

Do not run imported legacy code directly. Start by reading:

1. `docs/diagnosis.md`
2. `docs/safety-model.md`
3. `docs/improvement-plan.md`
4. `docs/rebrand-plan.md`

When legacy code is added, first perform static analysis and remove dangerous defaults before creating any installer.

## Ethical notice

Security knowledge is powerful. This project exists to help people defend systems, understand risks, and learn responsibly. It must not be used to harm, intimidate, spy on, disrupt, or access systems without permission.
