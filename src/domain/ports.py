"""
src/domain/ports.py
Contratos (Protocols) que desacoplam o serviço de chat das tecnologias
concretas de embedding, armazenamento vetorial e geração de texto.

Qualquer adapter (Chroma, Groq, Ollama, FAISS, etc.) só precisa implementar
estas interfaces para ser plugado no ChatService, sem alterar a lógica de
negócio. Isso é o que permite trocar Groq <-> Ollama sem tocar em src/chat/.
"""
from __future__ import annotations

from typing import Protocol

from src.domain.entities import ChatMessage, DocumentChunk, RetrievedChunk


class EmbeddingModel(Protocol):
    """Converte textos em vetores numéricos."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class VectorStore(Protocol):
    """Armazena e recupera DocumentChunks por similaridade semântica."""

    def upsert(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        ...

    def query(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        ...

    def is_empty(self) -> bool:
        ...


class LLMClient(Protocol):
    """Gera texto a partir de um prompt de sistema e um histórico de mensagens."""

    def complete(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        ...
