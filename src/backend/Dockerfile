# ==========================================
# ETAPA 1: Builder (Compilación y Preparación)
# ==========================================
# Usamos Python 3.11. Esta versión tiene wheels para TODO.
FROM python:3.11-slim-bookworm AS builder

# Traemos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Variables de entorno para uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Instalamos dependencias mínimas para construir
# (Aunque con Python 3.11 casi todo bajará pre-compilado, prevenimos errores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements
COPY requirements.txt .

# Creamos el entorno virtual y rellenamos
# --no-cache es vital para no guardar los zips descargados
RUN uv venv /app/.venv && \
    uv pip install --no-cache -r requirements.txt

# ==========================================
# ETAPA 2: Final (Producción - Slim)
# ==========================================
FROM python:3.11-slim-bookworm

WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    # Agregamos el venv al PATH del sistema
    PATH="/app/.venv/bin:$PATH"

# Dependencias de Runtime (Mínimas para que corra Linux)
# libexpat1 es común para xml, libgomp1 para algunas libs de matemáticas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario non-root (Puntos extra DevOps)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# --- COPIA MAESTRA ---
# Solo copiamos el entorno virtual ya instalado desde la etapa builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copiamos tu código
COPY --chown=appuser:appgroup . .

# Usamos el usuario seguro
USER appuser

EXPOSE 8000

# Tu comando de arranque
CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--log-config", "logging.yaml"]