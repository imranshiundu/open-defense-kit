# Contributing to Open Defense Kit

Thank you for helping build a safer defensive security toolkit.

## Contribution standard

All contributions must support authorized, ethical, defensive, or lab-only security work.

Do not submit code that enables:

- phishing real users
- credential theft
- DDoS
- RAT/C2 operations
- payload deployment
- unauthorized exploitation
- surveillance of private devices or accounts

## Module requirements

Every module must include:

- name
- description
- category
- risk level
- required permission statement
- safe target examples
- unsafe target examples
- dependencies
- dry-run support where possible
- documentation

## Code requirements

Prefer:

- Python standard library where possible
- explicit subprocess argument arrays
- no shell=True unless absolutely justified
- no root requirement by default
- no hidden network activity
- no automatic remote script execution
- clear error handling

Avoid:

- `os.system()`
- curl-pipe-shell installs
- unpinned dependencies
- broad delete commands
- hidden telemetry
- commands that run without user review

## Documentation requirements

Every feature must explain:

1. what it does
2. when it is legal to use
3. how to use it safely
4. what risks it creates
5. how to test it in a lab

## Pull request checklist

- [ ] The feature is defensive, educational, or lab-only
- [ ] Dangerous behavior is not enabled by default
- [ ] The module has metadata
- [ ] The module has docs
- [ ] The module has tests where applicable
- [ ] The code does not require root by default
- [ ] The code avoids raw shell execution
- [ ] The README or docs were updated
