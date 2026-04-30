# Safety Model

Open Defense Kit uses a defense-first safety model. The project should assume that security tools are dual-use and must be handled with explicit boundaries.

## Risk levels

### Low risk

Safe educational or local-only actions.

Examples:

- reading documentation
- listing modules
- checking local dependencies
- scanning local source code for secrets
- viewing defensive checklists

### Medium risk

Actions that interact with owned systems or produce security-sensitive output.

Examples:

- scanning your own web app headers
- auditing your own container images
- checking your own cloud account configuration
- passive OSINT on your own domain

### High risk

Actions that could be misused or disrupt systems if pointed at unauthorized targets.

Examples:

- active network scanning
- authentication testing in a lab
- exploit simulation in a local vulnerable VM
- wireless testing in an isolated lab

### Prohibited

Actions that Open Defense Kit should not automate.

Examples:

- phishing real people
- credential theft
- DDoS
- RAT/C2 operations
- payload deployment
- unauthorized exploitation
- spying through cameras or devices

## Permission gate

Before medium/high-risk modules run, the CLI should require confirmation:

```text
I confirm that I own this target or have explicit written permission to test it.
```

The user should also see:

- module name
- risk level
- target
- expected network activity
- logs location
- safe-use warning

## Target rules

Allowed target patterns:

- localhost
- private lab IPs
- user-owned domains
- explicitly configured lab hosts
- CTF/lab environments with permission

Blocked or warning target patterns:

- random public IPs
- banking, government, telecom, hospital, school, or infrastructure domains
- social media platforms
- third-party SaaS services
- targets outside declared scope

## Install rules

Open Defense Kit should not install arbitrary third-party repositories by default.

Approved install paths:

- package manager packages from trusted sources
- pinned Python packages
- verified release artifacts
- documented manual installs
- optional module adapters that do not auto-execute cloned code

Blocked install patterns:

- blind `git clone && bash install.sh`
- automatic sudo commands
- downloading and executing remote scripts
- curl-pipe-shell installs
- unpinned dependencies for security-sensitive modules

## Logging

The tool should log:

- timestamp
- module name
- risk level
- target
- confirmation status
- command preview
- result path

Logs must not store secrets, passwords, tokens, cookies, or private keys.

## Default mode

Default mode should be safe and non-invasive:

- no root
- no auto-install
- dry-run available
- local-only first
- defensive modules first
- clear warnings

## Legacy import rule

No legacy module is trusted by default.

Each imported module must pass:

1. static review
2. category classification
3. risk classification
4. dependency review
5. command review
6. documentation review
7. test coverage
8. maintainer approval
