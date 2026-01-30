FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio de configuración
RUN mkdir -p ~/.streamlit

# Configurar Streamlit para App Runner
RUN echo '\
[server]\n\
port = 8501\n\
address = "0.0.0.0"\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
enableWebsocketCompression = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
' > ~/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "src/frontend/dashboard.py", \
      "--server.port=8501", \
      "--server.address=0.0.0.0", \
      "--server.headless=true"]