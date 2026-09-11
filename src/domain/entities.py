"""
src/domain/entities.py
Entidades e objetos de valor do domínio do chatbot.

Não dependem de nenhuma tecnologia de infraestrutura (Chroma, Groq, Streamlit).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ChatMessage:
    """Uma mensagem trocada entre usuário e chatbot."""
    role: Role
    content: str


@dataclass(frozen=True)
class DocumentChunk:
    """Um pedaço de texto indexado, pronto para ser recuperado pelo RAG."""
    id: str
    text: str
    source_title: str
    source_path: str


@dataclass(frozen=True)
class RetrievedChunk:
    """Um DocumentChunk recuperado para uma pergunta, com seu score de similaridade."""
    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class Source:
    """Referência de fonte exibida ao usuário junto da resposta."""
    title: str
    path: str
    snippet: str


@dataclass(frozen=True)
class ChatAnswer:
    """Resposta final do chatbot, já pronta para exibição na interface."""
    text: str
    sources: list[Source] = field(default_factory=list)
    context_found: bool = True
