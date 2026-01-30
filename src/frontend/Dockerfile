FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
      apt-get install -y --no-install-recommends curl && \
      rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY src/frontend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir -r requirements.txt

# Copiar configuración de Streamlit
RUN mkdir -p /root/.streamlit
COPY src/frontend/.streamlit/config.toml /root/.streamlit/config.toml

# Copiar código de la aplicación
COPY src/frontend/dashboard.py .

# Variables de entorno críticas para WebSocket
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
      CMD curl -f http://localhost:8080/_stcore/health || exit 1

CMD ["streamlit", "run", "dashboard.py", \
      "--server.port=8080", \
      "--server.address=0.0.0.0", \
      "--server.headless=true", \
      "--server.runOnSave=false", \
      "--server.enableCORS=false", \
      "--server.enableXsrfProtection=false", \
      "--browser.serverAddress=0.0.0.0", \
      "--browser.gatherUsageStats=false"]