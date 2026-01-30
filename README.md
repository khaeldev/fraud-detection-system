# 🛡️ AI Fraud Detection System

**Multi‑Agent Architecture for Financial Fraud Detection**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)](https://langchain-ai.github.io/langgraph/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-232F3E)](https://aws.amazon.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991)](https://openai.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B)](https://streamlit.io/)



Sistema avanzado de **detección de fraude financiero** basado en una **arquitectura multi‑agente orquestada con LangGraph**. Diseñado para evaluar **casos ambiguos** mediante razonamiento deductivo, recuperación de conocimiento interno (RAG) e inteligencia externa simulada, con **observabilidad completa y human‑in‑the‑loop**.

---

## 📋 Tabla de Contenidos

* [Arquitectura del Sistema](#-arquitectura-del-sistema)
* [Características Principales](#-características-principales)
* [Estructura del Proyecto](#-estructura-del-proyecto)
* [Instalación y Configuración](#-instalación-y-configuración)
* [Uso y Ejecución](#️-uso-y-ejecución)
* [Observabilidad (LangSmith)](#-observabilidad-langsmith)
* [Despliegue (Docker & Cloud)](#-despliegue-docker--cloud)
* [Decisiones de Diseño](#-decisiones-de-diseño)
* [Roadmap](#-roadmap)
* [Licencia](#-licencia)

---

## 🏗 Arquitectura del Sistema

El sistema utiliza **LangGraph** para modelar un **grafo de estados cíclico**, permitiendo:

* Decisiones no lineales
* Reintentos controlados
* Manejo de fallos (fallbacks)
* Escalamiento a revisión humana (HITL)

### 🔁 Flujo de Agentes (Implementación Real)

Los siguientes agentes corresponden **1:1 con la implementación en `agents.py`**:

1. **transaction_context_agent**
   Aplica reglas determinísticas iniciales sobre la transacción (monto, hora, dispositivo) y genera `internal_signals`.

2. **behavioral_pattern_agent**
   Analiza anomalías comparando la transacción contra el perfil histórico del cliente utilizando un LLM.

3. **internal_policy_rag_agent**
   Consulta políticas internas de fraude mediante RAG (FAISS + Embeddings) y retorna contexto normativo relevante.

4. **external_threat_intel_agent**
   Simula inteligencia externa para detectar comercios o patrones con reportes recientes de fraude.

5. **evidence_aggregator_agent**
   Nodo de convergencia que consolida señales internas, análisis conductual, políticas e inteligencia externa.

6. **debate_agent**
   Ejecuta razonamiento adversarial generando un debate **Pro-Fraude vs. Pro-Cliente** para mitigar sesgos del modelo.

7. **decision_arbiter_agent**
   Emite la decisión final en formato estructurado:

   * `APPROVE`
   * `CHALLENGE`
   * `BLOCK`
   * `ESCALATE_TO_HUMAN`

8. **explainability_agent**
   Genera explicaciones diferenciadas para **cliente final** y **auditoría interna**, garantizando trazabilidad y cumplimiento regulatorio.

---

## ✨ Características Principales

* **Arquitectura Multi‑Agente Real** (no chain-of-thought lineal)
* **Multi‑Provider AI**

  * AWS Bedrock (Claude 3 Sonnet / Haiku)
  * OpenAI (GPT‑4o)
  * Azure OpenAI
* **RAG Persistente**

  * FAISS en disco para menor latencia y costos
* **Alta Disponibilidad**

  * Fallback automático a modo *Mock* ante throttling o caída del LLM
* **Human‑in‑the‑Loop (HITL)**

  * Escalamiento manual en casos de baja confianza
* **Observabilidad End‑to‑End**

  * Trazabilidad completa con LangSmith
* **Production‑Ready**

  * Docker, separación Backend / Frontend, despliegue cloud

---

## 📂 Estructura del Proyecto

```text
fraud-detection-system/
├── .env                    # Variables de entorno
├── pyproject.toml          # Dependencias (uv / poetry compatible)
├── uv.lock                 # Lockfile
├── README.md               # Documentación
├── Dockerfile              # Imagen Backend
├── docker-compose.yml      # Orquestación local
├── src/
│   ├── backend/
│   │   ├── app.py          # API Gateway (FastAPI)
│   │   ├── agents.py       # Grafo y lógica multi-agente
│   │   ├── rag_engine.py   # Motor RAG (FAISS)
│   │   ├── data.py         # Datos sintéticos y perfiles
│   │   └── utils.py        # Utilidades
│   └── frontend/
│       └── dashboard.py    # UI Operador (Streamlit)
└── faiss_store_openai/     # Persistencia vectorial (auto-generada)
```

---

## 🚀 Instalación y Configuración

Este proyecto utiliza **uv** para una gestión de dependencias rápida y reproducible.

### 1. Prerrequisitos

* Python **3.11+**
* Cuenta de **AWS Bedrock** o **OpenAI**
* Docker (opcional, para despliegue)

Instalar **uv**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clonar e Instalar Dependencias

```bash
git clone https://github.com/tu-usuario/fraud-detection-system.git
cd fraud-detection-system
uv sync
```

### 3. Configuración de Entorno

Crear un archivo `.env` en la raíz:

```env
# --- LLM PROVIDER (aws | openai | azure) ---
LLM_PROVIDER="openai"

# --- OPENAI ---
OPENAI_API_KEY="sk-proj-..."

# --- LANGSMITH ---
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="lsv2_..."
LANGCHAIN_PROJECT="fraud-detection-prod"

# --- AWS BEDROCK ---
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="..."
AWS_DEFAULT_REGION="us-east-1"
```

---

## ▶️ Uso y Ejecución

El sistema consta de **Backend (API)** y **Frontend (Dashboard)**.

### 1. Backend – FastAPI

```bash
uv run uvicorn src.backend.app:app --reload --port 8000 --log-config src/backend/logging.yaml
```

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend – Streamlit

```bash
uv run streamlit run src/frontend/dashboard.py
```

* Dashboard: [http://localhost:8501](http://localhost:8501)

---

## 🔍 Observabilidad (LangSmith)

El sistema envía trazas detalladas a **LangSmith**:

* Input del usuario
* Decisión de cada agente
* Tokens consumidos
* Latencia por nodo
* Resultado final

**Flujo de validación:**

1. Ejecuta una transacción desde el dashboard
2. Ingresa a `smith.langchain.com`
3. Abre el proyecto `fraud-detection-system`

---

## 🐳 Despliegue (Docker & Cloud)

### 1. Build de Imagen

```bash

docker build -t fraud-detection-system -f src/backend/Dockerfile .
```

---

### 2. ☁️ Terraform – Infraestructura como Código (IaC)

Integrado con Actions se realiza el deploy mediante terraform (package infra).

Los siguientes comandos permiten **provisionar infraestructura cloud reproducible** (ECR, App Runner / ECS, IAM, networking).

Inicializar Terraform:

```bash
terraform init
```

Validar configuración:

```bash
terraform validate
```

Formatear archivos:

```bash
terraform fmt
```

Planificar cambios:

```bash
terraform plan -out=tfplan
```

Aplicar infraestructura:

```bash
terraform apply tfplan
```

Destruir recursos (cleanup):

```bash
terraform destroy
```

---

### 3. Cloud (AWS)

* Subir imagen a **Amazon ECR**
* Desplegar en:

  * **AWS App Runner** (autoscaling simple)
  * **ECS Fargate** (mayor control)
* FAISS puede:

  * Regenerarse al inicio
  * Persistirse vía **EFS / S3**

---

## Frontend

Si no encuentras el servicio disponible, es porque fue dado de baja debido a costos operativos.
https://frauddetectionapp1.streamlit.app/

## 🧠 Decisiones de Diseño

* **LangGraph vs Chains** → Control de flujo explícito y escalable
* **FAISS Local** → Menor latencia y costos
* **Debate Adversarial** → Reducción de sesgos del LLM
* **Fallback Mock** → Continuidad operativa garantizada

---

---

TEST CASES:
- APPROVE: T-LEGIT-001

```json
{
   "decision":"APPROVE",
   "confidence":0.95,
   "signals":{
      "high_amount":false,
      "odd_hours":false,
      "new_device":true
   },
   "citations_internal":[
      "FP-01: Si el monto de la transacción supera 3 veces el promedio histórico del cliente y se realiza fuera de su horario habitual, se debe emitir un CHALLENGE.",
      "FP-02: Cualquier transacción realizada desde un país diferente al habitual y usando un dispositivo no registrado previamente debe ser escalada inmediatamente a revisión humana (ESCALATE_TO_HUMAN)."
   ],
   "citations_external":"Comercio verificado y seguro (Whitelisted).",
   "explanation_customer":"Su transacción ha sido aprobada porque proviene de un comercio verificado, lo que significa que es un lugar confiable para realizar compras. Además, nuestro análisis ha determinado que el riesgo asociado a esta transacción es bajo, lo que nos permite proceder con confianza.",
   "explanation_audit":"La decisión de aprobar la transacción se basa en un alto nivel de confianza (0.95) y en el hecho de que el comercio está en nuestra lista blanca. El análisis de riesgo ha indicado que no hay preocupaciones significativas, lo que justifica la aprobación."
}
```

- FRAUD: T-FRAUD-999

```json
{
   "decision":"BLOCK",
   "confidence":1.0,
   "signals":{
      "high_amount":true,
      "odd_hours":true,
      "new_device":true
   },
   "citations_internal":[
      "FP-01: Si el monto de la transacción supera 3 veces el promedio histórico del cliente y se realiza fuera de su horario habitual, se debe emitir un CHALLENGE.",
      "FP-02: Cualquier transacción realizada desde un país diferente al habitual y usando un dispositivo no registrado previamente debe ser escalada inmediatamente a revisión humana (ESCALATE_TO_HUMAN)."
   ],
   "citations_external":"ALERTA CRÍTICA (NIVEL ROJO): Este comercio está en la lista negra global de lavado de activos. BLOQUEO OBLIGATORIO.",
   "explanation_customer":"Su transacción ha sido bloqueada porque está relacionada con un comercio que se encuentra en la lista negra global de lavado de activos. Esto significa que hay un riesgo significativo asociado, y es nuestra responsabilidad proteger su seguridad financiera.",
   "explanation_audit":"La decisión de bloquear la transacción se basa en un riesgo crítico identificado, ya que el comercio involucrado está en la lista negra global de lavado de activos. La confianza en esta decisión es del 100%, lo que justifica la acción preventiva para mitigar riesgos legales y financieros."
}
```

- CUSTOM: T-1002

```json
{
   "decision":"CHALLENGE",
   "confidence":0.7,
   "signals":{
      "high_amount":true,
      "odd_hours":false,
      "new_device":true
   },
   "citations_internal":[
      "FP-01: Si el monto de la transacción supera 3 veces el promedio histórico del cliente y se realiza fuera de su horario habitual, se debe emitir un CHALLENGE.",
      "FP-02: Cualquier transacción realizada desde un país diferente al habitual y usando un dispositivo no registrado previamente debe ser escalada inmediatamente a revisión humana (ESCALATE_TO_HUMAN)."
   ],
   "citations_external":"ALERTA: Reportes de fraude recientes en este comercio.",
   "explanation_customer":"Hemos decidido desafiar la transacción debido a que el monto es inusual y hemos recibido reportes recientes de fraude. Esto significa que necesitamos realizar una revisión más detallada antes de poder confirmar la validez de la transacción.",
   "explanation_audit":"La decisión de desafiar la transacción se basa en un nivel de confianza del 70%, lo que indica que hay razones suficientes para sospechar de la legitimidad de la operación. La inusualidad del monto y los reportes de fraude recientes justifican una auditoría más exhaustiva para mitigar riesgos."
}
```

- ESCALATE_TO_HUMAN: T-HUMAN-999

```json
{
   "decision":"ESCALATE_TO_HUMAN",
   "confidence":0.5,
   "signals":{
      "high_amount":false,
      "odd_hours":false,
      "new_device":true
   },
   "citations_internal":[
      "FP-01: Si el monto de la transacción supera 3 veces el promedio histórico del cliente y se realiza fuera de su horario habitual, se debe emitir un CHALLENGE.",
      "FP-02: Cualquier transacción realizada desde un país diferente al habitual y usando un dispositivo no registrado previamente debe ser escalada inmediatamente a revisión humana (ESCALATE_TO_HUMAN)."
   ],
   "citations_external":"Sin reportes negativos.",
   "explanation_customer":"Su transacción ha sido escalada para revisión humana debido a que se realizó en un país diferente y el monto es alto. Esto se hace para garantizar la seguridad de su cuenta y prevenir posibles fraudes.",
   "explanation_audit":"La decisión de escalar la transacción a un humano se basa en un nivel de confianza del 50%, considerando el riesgo potencial asociado a transacciones internacionales de alto monto, conforme a las políticas de prevención de fraude."
}
```



## 📄 Licencia

Este proyecto se distribuye bajo la licencia **Apache 2.0**.

---
## Aviso sobre la licencia

Este repositorio se proporciona únicamente con fines de evaluación técnica.
La implementación tiene un alcance y una simplicidad intencionados.

Cualquier uso que vaya más allá de la evaluación requiere el permiso explícito por escrito del autor.
---
**Autor:** Kenny Julián Luque Ticona
**Stack:** Python · LangGraph · AWS · FastAPI · Streamlit


terraform init
terraform state list
terraform taint aws_apprunner_service.app