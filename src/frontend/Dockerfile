FROM python:3.11-slim-bookworm

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY src/frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente
COPY src/frontend/ ./src/frontend/

# Crear directorio de config y copiar configuración
RUN mkdir -p /root/.streamlit
COPY src/frontend/.streamlit/config.toml /root/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/frontend/dashboard.py", \
      "--server.port=8501", \
      "--server.address=0.0.0.0", \
      "--server.headless=true"]