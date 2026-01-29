import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="Sistema IA Detección de Fraude", layout="wide")

API_URL = "http://localhost:8000"

st.title("🛡️ Sistema Multi-Agente: Detección de Fraude Ambiguo")

st.sidebar.header("Simulación")
tx_options = requests.get(f"{API_URL}/test-data").json()
tx_ids = [t["transaction_id"] for t in tx_options]
selected_tx_id = st.sidebar.selectbox("Seleccionar Transacción", tx_ids)

selected_tx = next(t for t in tx_options if t["transaction_id"] == selected_tx_id)

st.sidebar.json(selected_tx)

if st.sidebar.button("Analizar Transacción"):
    with st.spinner('Orquestando agentes (Contexto -> RAG -> Web -> Debate -> Decisión)...'):
        try:
            response = requests.post(f"{API_URL}/analyze", json=selected_tx)
            result = response.json()
            
            # --- Layout de Resultados ---
            col1, col2, col3 = st.columns(3)
            
            # Indicador de Decisión
            decision = result["decision"]
            color = "green" if decision == "APPROVE" else "red" if decision == "BLOCK" else "orange"
            
            with col1:
                st.markdown(f"### Decisión: :{color}[{decision}]")
                st.metric("Confianza IA", f"{result['confidence']*100:.1f}%")
            
            with col2:
                st.info("Políticas Aplicadas (RAG)")
                for p in result["details"]["policies"]:
                    st.write(f"- {p}")

            with col3:
                st.warning("Intel Externa")
                st.write(result["details"]["intel"])
            
            st.divider()
            
            # Detalle del Debate y Explicación
            tab1, tab2, tab3 = st.tabs(["🗣️ Debate de Agentes", "📄 Explicación Cliente/Auditoría", "🔍 Señales Internas"])
            
            with tab1:
                st.markdown(result["details"]["debate"])
                
            with tab2:
                st.subheader("Para el Cliente:")
                st.write(result["explanations"]["explanation_customer"])
                st.subheader("Para Auditoría:")
                st.write(result["explanations"]["explanation_audit"])
                
            with tab3:
                st.json(result["details"]["signals"])

            # --- Human in the Loop (HITL) ---
            if decision == "ESCALATE_TO_HUMAN" or decision == "CHALLENGE":
                st.divider()
                st.header("👤 Revisión Humana Requerida")
                human_col1, human_col2 = st.columns(2)
                with human_col1:
                    if st.button("Aprobar Manualmente", type="primary"):
                        st.success("Transacción Aprobada por Operador")
                        # Aquí iría llamada a API para actualizar DB
                with human_col2:
                    if st.button("Bloquear Manualmente"):
                        st.error("Transacción Bloqueada por Operador")

        except Exception as e:
            st.error(f"Error en el análisis: {e}")