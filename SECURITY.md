# Security Policy

## Purpose

Open Defense Kit is an ethical, legal, defense-first project. Security issues, unsafe modules, dangerous defaults, and misuse-enabling behavior should be reported and fixed quickly.

## Supported scope

Security reports are welcome for:

- unsafe command execution
- dependency risks
- accidental secret exposure
- dangerous defaults
- modules that enable abuse
- missing authorization checks
- documentation that encourages illegal use
- supply-chain risks

## Prohibited project behavior

The project should not include working automation for:

- phishing real users
- credential theft
- DDoS
- botnets
- RAT/C2 operations
- unauthorized exploitation
- spying on cameras, microphones, devices, or accounts
- bypassing authentication on systems without permission

## Reporting

Open an issue with:

- summary
- affected file/module
- risk level
- reproduction steps, if safe
- suggested fix

Do not include real secrets, real victim data, stolen credentials, private keys, or exploit output from unauthorized targets.

## Maintainer response

Reports should be triaged into:

- documentation issue
- safety issue
- dependency issue
- code issue
- prohibited functionality

High-risk prohibited functionality should be removed or disabled by default.

## Safe disclosure rule

Do not publish weaponized details in issues. Keep reports focused on how to make the project safer.
