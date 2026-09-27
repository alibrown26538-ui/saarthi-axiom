FROM debian:bookworm-slim AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV ELAN_HOME="/root/.elan"
ENV PATH="${ELAN_HOME}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.6.0

WORKDIR /workspace

COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 10001 saarthi && chown -R saarthi:saarthi /workspace
USER saarthi

ENTRYPOINT ["pytest", "tests/"]
