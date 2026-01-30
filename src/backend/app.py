from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agents import app_graph, AgentState
from .data import get_customer_profile, TRANSACTIONS
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)


app = FastAPI(title="AI Fraud Detection System")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    country: str
    channel: str
    device_id: str
    timestamp: str
    merchant_id: str
    customer_id: str

@app.post("/analyze")
async def analyze_transaction(tx: TransactionRequest):
    profile = get_customer_profile(tx.customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    initial_state:AgentState = {
        "transaction": tx.dict(),
        "customer_profile": profile,
        "internal_signals": {},
        "behavior_analysis": "",
        "policy_context": [],
        "external_intel": "",
        "debate_transcript": "",
        "final_decision": {},
        "explanation": {}
    }
    
    logger.info("🚀 Iniciando análisis de transacción...")
    result = app_graph.invoke(initial_state)
    
    response = {
        "transaction_id": tx.transaction_id,
        "decision": result["final_decision"]["decision"],
        "confidence": result["final_decision"]["confidence"],
        "details": {
            "signals": result["internal_signals"],
            "intel": result["external_intel"],
            "debate": result["debate_transcript"],
            "policies": result["policy_context"]
        },
        "explanations": result["explanation"]
    }
    

    custom_response = {
        "decision": result["final_decision"].get("decision", "MANUAL_REVIEW"),
        "confidence": result["final_decision"].get("confidence", 0.0),
        "signals": result["internal_signals"],
        "citations_internal": result["policy_context"],
        "citations_external": result["external_intel"],
        "explanation_customer": result["explanation"].get("explanation_customer", ""),
        "explanation_audit": result["explanation"].get("explanation_audit", "")
    }
    logger.info(f"✅ Análisis completado custom_response: {custom_response}")

    logger.info(f"✅ Análisis completado: {response}")
    return response

@app.get("/test-data")
def get_test_data():
    return TRANSACTIONS