FROM python:3.12-slim

# Install system build dependencies (needed for nebula3-python C extensions)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Prevent uv from downloading isolated Python builds
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# ===== Layer 1: Dependencies only (cached until pyproject.toml or uv.lock change) =====
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml shared/
COPY web/pyproject.toml web/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-workspace

# ===== Layer 2: Source code =====
COPY shared/ shared/
COPY web/ ./

# ===== Layer 3: Install workspace members (shared as package, web as virtual) =====
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Clean up build dependencies (reduce image size)
RUN apt-get remove -y build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "main.py"]