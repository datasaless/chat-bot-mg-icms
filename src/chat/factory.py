"""
src/chat/factory.py
Ponto único de montagem (composition root) do ChatService com seus adapters
concretos, escolhidos conforme a configuração em settings.py.

Isolar esta montagem aqui é o que permite trocar Groq <-> Ollama, ou o
modelo de embeddings, sem alterar app.py nem chat_service.py.
"""
from __future__ import annotations

from src.chat.chat_service import ChatService
from src.config.settings import CHROMA_DB_DIR, settings
from src.domain.ports import LLMClient
from src.ingestion.embedder import SentenceTransformerEmbedder
from src.retrieval.chroma_store import ChromaVectorStore


def _build_llm_client() -> LLMClient:
    if settings.llm_provider == "ollama":
        from src.generation.ollama_client import OllamaLLMClient

        return OllamaLLMClient(settings.ollama_base_url, settings.ollama_model)

    from src.generation.groq_client import GroqLLMClient

    return GroqLLMClient(settings.groq_api_key, settings.groq_model)


def build_chat_service() -> ChatService:
    embedder = SentenceTransformerEmbedder(settings.embedding_model_name)
    vector_store = ChromaVectorStore(CHROMA_DB_DIR, settings.collection_name)
    llm_client = _build_llm_client()

    return ChatService(
        embedder=embedder,
        vector_store=vector_store,
        llm_client=llm_client,
        top_k=settings.top_k,
    )
