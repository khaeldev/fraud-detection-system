from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from src.backend.data import FRAUD_POLICIES

import os
import time
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🎛️ SELECTOR DE PROVEEDOR (SWITCH)
# ==========================================
# Opciones disponibles: "aws", "openai", "azure", "mock"
EMBEDDING_PROVIDER = "openai" 

BATCH_SIZE = 10
BATCH_SLEEP = 1.0 

FAISS_PATH = f"tmp/faiss_store_{EMBEDDING_PROVIDER}"

# ==========================================
# 1. CLASE MOCK (Fallback de seguridad)
# ==========================================
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Dimensión 1536 (estándar OpenAI) simulada
        return [np.random.rand(1536).tolist() for _ in texts]
    def embed_query(self, text: str) -> List[float]:
        return np.random.rand(1536).tolist()

# ==========================================
# 2. FACTORY: OBTENER EL MODELO
# ==========================================
def get_embedding_model():
    """Devuelve el modelo configurado según el SWITCH."""
    try:
        if EMBEDDING_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            print("🔵 Usando OpenAI Embeddings (text-embedding-3-small)...")
            return OpenAIEmbeddings(model="text-embedding-3-small")
        
        elif EMBEDDING_PROVIDER == "azure":
            from langchain_openai import AzureOpenAIEmbeddings
            print("☁️ Usando Azure OpenAI Embeddings...")
            return AzureOpenAIEmbeddings(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                model="text-embedding-3-small"
            )

        elif EMBEDDING_PROVIDER == "aws":
            from langchain_aws import BedrockEmbeddings
            import boto3
            from botocore.config import Config
            
            print("🟠 Usando AWS Bedrock (Titan V2)...")
            retry_config = Config(
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                retries={"max_attempts": 5, "mode": "adaptive"}
            )
            boto3_session = boto3.Session(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
                region_name="us-east-1"
            )
            return BedrockEmbeddings(
                client=boto3_session.client("bedrock-runtime", config=retry_config),
                model_id="amazon.titan-embed-text-v2:0"
            )
            
        else:
            print("⚠️ Modo Mock seleccionado manualmente.")
            return MockEmbeddings()

    except Exception as e:
        print(f"❌ Error inicializando {EMBEDDING_PROVIDER}: {e}")
        print("⚠️ Fallback automático a MOCK.")
        return MockEmbeddings()

# ==========================================
# 3. MOTOR RAG
# ==========================================
class RAGEngine:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        
        # 1. Obtenemos el modelo seleccionado
        self.embeddings = get_embedding_model()

        # 2. Intentar cargar desde disco (Caché)
        if os.path.exists(FAISS_PATH):
            print(f"📦 Cargando índice existente desde: {FAISS_PATH}...")
            try:
                self.vector_store = FAISS.load_local(
                    FAISS_PATH,
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✅ Índice cargado correctamente.")
            except Exception as e:
                print(f"⚠️ Error cargando disco (quizás cambió el proveedor): {e}")
                print("🔄 Se regenerará el índice.")

        # 3. Si no existe o falló la carga, generamos de cero
        if not self.vector_store:
            print(f"🚀 Generando embeddings nuevos con {EMBEDDING_PROVIDER}...")
            self._build_index()

        # 4. Configurar el retriever
        if self.vector_store:
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

    def _build_index(self):
        docs = [
            Document(
                page_content=p["text"],
                metadata={"policy_id": p["policy_id"], "rule": p["rule"]}
            )
            for p in FRAUD_POLICIES
        ]
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]

        try:
            # Procesamiento por lotes para evitar Timeouts
            all_vectors = []
            total = len(texts)
            
            for i in range(0, total, BATCH_SIZE):
                batch = texts[i:i + BATCH_SIZE]
                print(f"   Processing batch {i} to {min(i+BATCH_SIZE, total)}...")
                
                vectors = self.embeddings.embed_documents(batch)
                all_vectors.extend(vectors)
                
                # SLEEP 
                if EMBEDDING_PROVIDER == "aws":
                    time.sleep(BATCH_SLEEP)

            # Crear FAISS con los vectores generados
            self.vector_store = FAISS.from_embeddings(
                text_embeddings=list(zip(texts, all_vectors)),
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            # Guardar en disco específico del proveedor
            self.vector_store.save_local(FAISS_PATH)
            print(f"💾 Índice guardado en: {FAISS_PATH}")

        except Exception as e:
            print(f"❌ Error generando embeddings con {EMBEDDING_PROVIDER}: {e}")
            print("⚠️ Usando MOCK temporalmente para no detener el sistema.")
            self.vector_store = FAISS.from_documents(docs, MockEmbeddings())

    def query(self, query_text: str):
        if self.retriever:
            try:
                return self.retriever.invoke(query_text)
            except Exception as e:
                print(f"Error querying RAG: {e}")
                return []
        return []

rag_engine = RAGEngine()