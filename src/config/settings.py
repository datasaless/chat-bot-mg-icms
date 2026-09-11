"""
src/config/settings.py
Configurações centrais do chatbot, lidas de variáveis de ambiente (.env).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_DOCS_DIR = BASE_DIR / "data" / "source_docs"
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"


@dataclass(frozen=True)
class Settings:
    # Provedor de LLM: "groq" (padrão, API rápida e barata) ou "ollama" (local)
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")

    # Groq
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    # llama-3.3-70b-versatile foi descontinuado pela Groq em ago/2026;
    # openai/gpt-oss-120b é o substituto recomendado pela própria Groq.
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Ollama (execução 100% local, sem custo de API)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # Embeddings — modelo multilíngue leve, roda em CPU sem custo
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Recuperação
    top_k: int = int(os.getenv("RAG_TOP_K", "4"))
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))

    collection_name: str = "uaiso_docs"


settings = Settings()
