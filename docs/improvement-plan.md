# Improvement Plan

This document defines how the unsafe legacy project should be transformed into Open Defense Kit.

## Phase 0: Quarantine

Before importing legacy code:

- do not run it on a main machine
- store it in a separate branch or `legacy/` folder
- mark it as untrusted
- do static analysis first
- remove dangerous commands before any installer exists

## Phase 1: Rebrand

Replace all offensive naming and language.

Required changes:

- `hackingtools` -> `Open Defense Kit`
- `hacking` command -> `odkit`
- offensive banners -> professional defensive UI
- attack-first categories -> defensive workflows
- root-first install instructions -> virtualenv/pipx/dev setup

## Phase 2: Remove unsafe defaults

Remove or disable by default:

- DDoS tools
- phishing frameworks
- RAT/C2 tools
- payload builders
- webcam/camera hacking modules
- credential attack modules against real accounts
- wireless attack modules that can disrupt networks
- blind install commands from unknown repositories

## Phase 3: Introduce module metadata

Every module must have a metadata file:

```yaml
name: example-module
category: defensive-audit
risk: low
requires_authorization: true
network_activity: passive
safe_targets:
  - localhost
  - owned domains
blocked_targets:
  - third-party systems without permission
installer: none
run_mode: guided
```

## Phase 4: Replace raw shell execution

Replace direct `os.system()` calls with a safer command runner that:

- logs commands
- blocks dangerous commands
- validates arguments
- supports dry-run mode
- avoids shell injection
- uses subprocess arrays instead of raw shell strings
- never uses sudo automatically

## Phase 5: Build the safe CLI

The CLI should include:

- `odkit modules list`
- `odkit modules info <name>`
- `odkit check-permission`
- `odkit doctor`
- `odkit run <safe-module> --target <owned-target>`
- `odkit lab init`

## Phase 6: Add safety gates

Before any network action:

- show the module risk
- ask the user to confirm ownership/permission
- show the exact command or action
- support dry-run mode
- save a local audit log

## Phase 7: Add tests

Minimum tests:

- unsafe command blocker tests
- metadata validation tests
- CLI route tests
- no-root installer test
- docs link checks
- module allowlist tests

## Phase 8: Documentation polish

Required docs:

- README
- ethical use cases
- safety model
- diagnosis report
- improvement plan
- rebrand plan
- module authoring guide
- legal disclaimer
- local lab setup guide

## Phase 9: Release discipline

Before release:

- tag versions
- pin dependencies
- add changelog
- add security policy
- add code of conduct
- publish checksums for release files
- add CI for linting and tests

## Definition of done

Open Defense Kit is ready only when:

- it can run without root
- dangerous modules are absent or disabled
- every module has metadata
- every network action requires authorization confirmation
- all docs are clear
- tests pass
- install/uninstall is safe
- it looks like a defensive project, not a hacking launcher
