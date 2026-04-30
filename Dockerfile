# syntax=docker/dockerfile:1
# Enables BuildKit features (cache mounts, faster builds)
FROM kalilinux/kali-rolling:latest

LABEL org.opencontainers.image.title="Open Defense Kit" \
      org.opencontainers.image.description="Ethical Security Toolkit and Learning Environment" \
      org.opencontainers.image.source="https://github.com/imranshiundu/open-defense-kit" \
      org.opencontainers.image.licenses="MIT"

# Install system dependencies
# - sudo and python3-venv are not needed (container runs as root, venv unused)
# - --no-install-recommends keeps the layer lean
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3-pip python3-venv curl wget php && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/open-defense-kit

# Copy requirements first so this layer is cached unless requirements change
COPY requirements.txt ./

# --mount=type=cache persists the pip cache across rebuilds (BuildKit only)
# --break-system-packages required on Kali (PEP 668 externally-managed env)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --break-system-packages -r requirements.txt

# Copy the rest of the source (respects .dockerignore)
COPY . .

# Ensure the tools directory exists for installs performed at runtime
RUN mkdir -p /root/.odk/tools

ENTRYPOINT ["python3", "/root/open-defense-kit/odk.py"]
