from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.backend.rag_engine import rag_engine
import json
import os
import boto3
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)
# ==========================================
# 🎛️ SELECTOR DE PROVEEDOR
# ==========================================
# Opciones: "aws", "openai", "groq", "mock"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# ==========================================
# 🔌 INICIALIZACIÓN DEL MODELO
# ==========================================
llm = None

try:
    if LLM_PROVIDER == "aws":
        from langchain_aws import ChatBedrock
        from botocore.config import Config
        
        retry_config = Config(
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            retries={'max_attempts': 5, 'mode': 'adaptive'}
        )
        boto3_session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        # Usamos Haiku o Sonnet
        llm = ChatBedrock(
            client=boto3_session.client("bedrock-runtime", config=retry_config),
            model="anthropic.claude-3-haiku-20240307-v1:0",
            temperature=0.1
        )
        logger.info("✅ Usando AWS Bedrock (Claude 3)")

    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        # gpt-4o-mini es barato, rápido e inteligente
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        logger.info("✅ Usando OpenAI (GPT-4o-mini)")

    elif LLM_PROVIDER == "groq":
        # from langchain_groq import ChatGroq
        # # Llama 3 70B es increíblemente rápido en Groq
        # llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.0)
        # logger.info("✅ Usando Groq (Llama 3)")
        pass

    else:
        raise Exception("Modo Mock seleccionado")

except Exception as e:
    logger.info(f"⚠️ Error cargando {LLM_PROVIDER}: {e}. Cambiando a MOCK.")
    llm = None # Esto activará el fallback manual más abajo

# ==========================================
# 🧠 HELPER: INVOKER UNIVERSAL
# ==========================================
def invoke_agent(system_prompt: str, user_prompt: str, mock_data: dict | str, force_json: bool = False):
    """
    Invoca al LLM seleccionado. Si falla o es None, usa Mock.
    """
    if llm is None:
        return mock_data

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        logger.info(f"💬 Respuesta LLM: {response}")
        content = response.content.strip() # type: ignore

        if force_json:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1]
            return json.loads(content.strip())
        
        return content

    except Exception as e:
        logger.info(f"❌ Error en llamada LLM: {e}")
        return mock_data

# ==========================================
# 🤖 AGENTS
# ==========================================

class AgentState(TypedDict):
    transaction: dict
    customer_profile: dict
    internal_signals: dict 
    behavior_analysis: str 
    policy_context: List[str] 
    external_intel: str 
    debate_transcript: str 
    final_decision: dict 
    explanation: dict 

def transaction_context_agent(state: AgentState):
    """Reglas simples."""
    tx = state["transaction"]
    try:
        hour = int(tx["timestamp"].split("T")[1].split(":")[0])
    except:
        hour = 12
    signals = {
        "high_amount": tx["amount"] > 3000, 
        "odd_hours": hour < 6 or hour > 23,
        "new_device": True 
    }
    return {"internal_signals": signals}

def behavioral_pattern_agent(state: AgentState):
    sys = """Eres un Analista de Fraude. Detecta anomalías en monto, hora y dispositivo.
    Reglas de Análisis:
    1. Si el monto es MUCHO MAYOR al promedio -> RIESGO ALTO.
    2. Si el monto es MENOR al promedio -> RIESGO BAJO (es normal gastar poco).
    3. Si el dispositivo es nuevo pero el monto es bajo -> RIESGO BAJO.
    4. Sé breve.
    """
    usr = f"Tx: {state['transaction']}. Perfil: {state['customer_profile']}. ¿Es anómalo?"
    mock = "Monto muy superior al promedio y dispositivo nuevo. Riesgo Alto."
    
    return {"behavior_analysis": invoke_agent(sys, usr, mock)}

def internal_policy_rag_agent(state: AgentState):
    try:
        query = f"Fraude transacción monto {state['transaction']['amount']}"
        docs = rag_engine.query(query)
        policies = [f"{d.metadata.get('policy_id', 'Unk')}: {d.page_content}" for d in docs]
        if not policies: policies = ["Sin políticas específicas."]
    except:
        policies = ["RAG no disponible."]
    return {"policy_context": policies}

def external_threat_intel_agent(state: AgentState):
    merchant = state["transaction"].get("merchant_id", "")
    if merchant == "M-002":
        intel = "ALERTA: Reportes de fraude recientes en este comercio."
    
    elif merchant == "M-DANGER":
        intel = "ALERTA CRÍTICA (NIVEL ROJO): Este comercio está en la lista negra global de lavado de activos. BLOQUEO OBLIGATORIO."
    
    elif merchant == "M-SAFE":
        intel = "Comercio verificado y seguro (Whitelisted)."

    else:
        intel = "Sin reportes negativos."
    return {"external_intel": intel}

def evidence_aggregator_agent(state: AgentState):
    return {}

def debate_agent(state: AgentState):
    sys = """Genera un debate corto entre un agente Pro-Fraude y uno Pro-Cliente.
    REGLA CLAVE:
    Si 'Intel Externa' dice "Whitelisted", "Seguro" o "Safe":
    - El Agente Pro-Fraude DEBE admitir que es seguro.
    - El Agente Pro-Cliente DEBE pedir aprobación inmediata.
    """
    usr = f"Datos: {state['transaction']}, Análisis: {state['behavior_analysis']}, Intel: {state['external_intel']}"
    mock = "Pro-Fraude: Riesgo alto por intel externa. Pro-Cliente: Es un cliente VIP. Conclusión: Verificar."
    
    return {"debate_transcript": invoke_agent(sys, usr, mock)}

def decision_arbiter_agent(state: AgentState):
    sys = """Eres el Juez de Riesgos.
    Tu decisión debe basarse en la evidencia más fuerte.
    Decide: APPROVE, CHALLENGE, BLOCK, ESCALATE_TO_HUMAN.    
    JERARQUÍA DE EVIDENCIA (De mayor a menor peso):
    1. [CRÍTICO] Intel Externa "Blacklisted" -> BLOCK.
    2. [FUERTE] Intel Externa "Whitelisted" + Dispositivo Conocido -> APPROVE.
    3. [MEDIO] Monto inusual o Dispositivo Nuevo -> CHALLENGE.
    
    Si todo parece normal (Monto bajo, Dispositivo conocido, Intel Neutra/Positiva) -> APPROVE.
    Para dudas -> "CHALLENGE" o "ESCALATE_TO_HUMAN".
    Responde SOLO JSON: {"decision": "str", "confidence": float, "reason": "str"}"""
    usr = f"Debate: {state['debate_transcript']}"
    mock = {"decision": "CHALLENGE", "confidence": 0.9, "reason": "Intel de fraude confirmada."}
    
    return {"final_decision": invoke_agent(sys, usr, mock, force_json=True)}

def explainability_agent(state: AgentState):
    sys = """Explica la decisión para cliente y auditoría.
    Responde SOLO JSON: {"explanation_customer": "str", "explanation_audit": "str"}"""
    usr = f"Decisión: {state['final_decision']}"
    mock = {"explanation_customer": "Validación requerida.", "explanation_audit": "Regla de Intel activada."}
    
    return {"explanation": invoke_agent(sys, usr, mock, force_json=True)}

# ==========================================
# 🕸️ GRAFO
# ==========================================
workflow = StateGraph(AgentState)
workflow.add_node("transaction_context_agent", transaction_context_agent)
workflow.add_node("behavioral_pattern_agent", behavioral_pattern_agent)
workflow.add_node("internal_policy_rag_agent", internal_policy_rag_agent)
workflow.add_node("external_threat_intel_agent", external_threat_intel_agent)
workflow.add_node("evidence_aggregator_agent", evidence_aggregator_agent)
workflow.add_node("debate_agent", debate_agent)
workflow.add_node("decision_arbiter_agent", decision_arbiter_agent)
workflow.add_node("explainability_agent", explainability_agent)

workflow.set_entry_point("transaction_context_agent")
workflow.add_edge("transaction_context_agent", "behavioral_pattern_agent")
workflow.add_edge("transaction_context_agent", "internal_policy_rag_agent")
workflow.add_edge("transaction_context_agent", "external_threat_intel_agent")
workflow.add_edge("behavioral_pattern_agent", "evidence_aggregator_agent")
workflow.add_edge("internal_policy_rag_agent", "evidence_aggregator_agent")
workflow.add_edge("external_threat_intel_agent", "evidence_aggregator_agent")
workflow.add_edge("evidence_aggregator_agent", "debate_agent")
workflow.add_edge("debate_agent", "decision_arbiter_agent")
workflow.add_edge("decision_arbiter_agent", "explainability_agent")
workflow.add_edge("explainability_agent", END)

app_graph = workflow.compile()