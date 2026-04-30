# Legacy Migration Map

This file tracks how legacy hacking-tool style features will be handled during the Open Defense Kit rebrand.

## Decision labels

| Label | Meaning |
|---|---|
| `KEEP_SAFE` | Already defensive and safe enough to keep with minor cleanup |
| `REWRITE_SAFE` | Useful idea, but must be rewritten safely under `odkit/` |
| `DOCS_ONLY` | Keep as explanation/checklist only; no automation |
| `LAB_ONLY_DOCS` | Explain only for isolated labs; no live-target automation |
| `REMOVE` | Not useful, broken, misleading, or too risky |
| `PROHIBITED` | Must not be automated or shipped |

## Initial category decisions

| Legacy category / feature type | Decision | Reason |
|---|---|---|
| Local file secret scanning | `REWRITE_SAFE` | Defensive, local-only, useful for developers |
| Dependency auditing | `REWRITE_SAFE` | Defensive and practical when scoped to owned projects |
| Container scanning | `REWRITE_SAFE` | Defensive when scoped to owned images |
| Cloud posture review | `REWRITE_SAFE` | Defensive when scoped to owned cloud accounts |
| Web security headers | `REWRITE_SAFE` | Defensive when scoped to owned domains |
| Passive OSINT for owned domains | `REWRITE_SAFE` | Useful with permission gates |
| Active recon/scanning | `LAB_ONLY_DOCS` | Can be disruptive; needs strict authorization gates before any automation |
| SQL injection tooling | `LAB_ONLY_DOCS` | Only acceptable in intentionally vulnerable labs or authorized assessments |
| Password cracking/bruteforce | `LAB_ONLY_DOCS` | High abuse risk; no real account automation |
| Wireless attack tooling | `LAB_ONLY_DOCS` | Can disrupt networks; no automation by default |
| Social engineering/phishing kits | `PROHIBITED` | Enables real-world harm |
| DDoS tools | `PROHIBITED` | Disruptive and illegal against third-party systems |
| RAT/C2 frameworks | `PROHIBITED` | Malware-like functionality |
| Payload builders | `PROHIBITED` | Enables unauthorized compromise |
| Camera/webcam hacking tools | `PROHIBITED` | Privacy-invasive and abuse-prone |
| Blind third-party tool installers | `REMOVE` | Supply-chain risk |
| Root-first installer | `REMOVE` | Unsafe default |
| Update script that deletes/reclones repo | `REMOVE` | Destructive and unsafe |

## Per-file review table

Populate this after importing legacy code into `legacy/original/`.

| File | Purpose | Risk | Decision | Notes |
|---|---|---:|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Migration rule

Safe functionality should be rewritten under `odkit/`. Legacy scripts should not be imported as runnable production code.
