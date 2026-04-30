<div align="center">

# Open Defense Kit (ODK)

**Ethical, Defense-First Security Toolkit & Learning Environment**

[![License](https://img.shields.io/github/license/imranshiundu/open-defense-kit?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali%20%7C%20Parrot%20%7C%20macOS-informational?style=flat-square)](#)
[![Stars](https://img.shields.io/github/stars/imranshiundu/open-defense-kit?style=flat-square)](https://github.com/imranshiundu/open-defense-kit/stargazers)
[![Issues](https://img.shields.io/github/issues/imranshiundu/open-defense-kit?style=flat-square)](https://github.com/imranshiundu/open-defense-kit/issues)

</div>

---

## Mission

Open Defense Kit is an ethical, legal, defense-first security toolkit project. It is being built as a safer replacement and rebrand for unsafe all-in-one hacking-tool launchers.

The goal is not to package offensive tools blindly. The goal is to create a controlled security learning and audit environment where every module is documented, permission-based, and safe by default.

## Non-negotiable Rule

**Use this project only on systems, accounts, networks, repositories, domains, and applications you own or have explicit written permission to test.**

Open Defense Kit will not be designed as a phishing kit, malware kit, botnet tool, DDoS tool, credential theft tool, RAT builder, or unauthorized exploitation framework.

---

## What's New in the ODK Rebrand

- **Defense-First Identity**: Shifted focus from "hacking tools" to security auditing and defensive learning.
- **Improved Hygiene**: All Python 2 code removed. OS-aware menus hide incompatible tools.
- **Safety Boundaries**: Tools install to `~/.odk/tools/` without requiring root permissions.
- **Clean Structure**: Modular codebase with shared UI themes and iterative navigation.
- **Container Security**: Official Docker support with Kali Linux base.

---

## Menu

{{toc}}

---

## Tools

{{tools}}

---

## Installation

### One-liner (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/imranshiundu/open-defense-kit/main/install.sh | sudo bash
```

This handles everything — installs prerequisites, clones the repo, sets up a venv, and creates the `odk` command.

### Manual install

```bash
git clone https://github.com/imranshiundu/open-defense-kit.git
cd open-defense-kit
sudo python3 install.py
```

Then run:
```bash
odk
```

## Docker

### Step 1 — Clone the repository

```bash
git clone https://github.com/imranshiundu/open-defense-kit.git
cd open-defense-kit
```

### Step 2 — Build the image

```bash
docker build -t odk .
```

### Step 3 — Run

**Option A — Direct (no Compose):**
```bash
docker run -it --rm odk
```

**Option B — With Docker Compose (recommended):**
```bash
# Start in background
docker compose up -d

# Open an interactive shell
docker exec -it odk bash

# Then launch the tool inside the container
python3 odk.py
```

---

## Contributing

Want a tool included? Ensure it fits the **Defensive/Auditing** mission and submit a PR.
See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Ethical Notice

Security knowledge is powerful. This project exists to help people defend systems, understand risks, and learn responsibly. It must not be used to harm, intimidate, spy on, disrupt, or access systems without permission.
