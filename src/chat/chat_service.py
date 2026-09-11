"""
src/chat/chat_service.py
Caso de uso principal: responder a pergunta do usuário usando RAG.

Depende apenas das portas do domínio (EmbeddingModel, VectorStore, LLMClient)
— nunca de Chroma, Groq ou Streamlit diretamente. Isso permite testar a
lógica de orquestração com dublês simples (fakes), sem rede nem modelos reais.
"""
from __future__ import annotations

from src.domain.entities import ChatAnswer, ChatMessage, Role, Source
from src.domain.ports import EmbeddingModel, LLMClient, VectorStore
from src.generation.prompt_templates import SYSTEM_PROMPT, build_user_prompt

MIN_RELEVANCE_SCORE = 0.15


class ChatService:
    def __init__(
        self,
        embedder: EmbeddingModel,
        vector_store: VectorStore,
        llm_client: LLMClient,
        top_k: int = 4,
    ) -> None:
        self._embedder = embedder
        self._vector_store = vector_store
        self._llm_client = llm_client
        self._top_k = top_k

    def ask(self, question: str, history: list[ChatMessage] | None = None) -> ChatAnswer:
        history = history or []

        if self._vector_store.is_empty():
            return ChatAnswer(
                text=(
                    "A base de conhecimento ainda não foi indexada. Rode "
                    "`python -m src.ingestion.build_index` antes de usar o chat."
                ),
                sources=[],
                context_found=False,
            )

        question_embedding = self._embedder.embed([question])[0]
        retrieved = self._vector_store.query(question_embedding, self._top_k)
        relevant = [r for r in retrieved if r.score >= MIN_RELEVANCE_SCORE]

        user_prompt = build_user_prompt(question, relevant)
        messages = [*history, ChatMessage(role=Role.USER, content=user_prompt)]

        answer_text = self._llm_client.complete(SYSTEM_PROMPT, messages)

        sources = [
            Source(
                title=item.chunk.source_title,
                path=item.chunk.source_path,
                snippet=_snippet(item.chunk.text),
            )
            for item in _deduplicate_by_source(relevant)
        ]

        return ChatAnswer(text=answer_text, sources=sources, context_found=bool(relevant))


def _snippet(text: str, max_length: int = 220) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= max_length else text[:max_length].rstrip() + "…"


def _deduplicate_by_source(retrieved):
    seen: set[str] = set()
    unique = []
    for item in retrieved:
        if item.chunk.source_path not in seen:
            seen.add(item.chunk.source_path)
            unique.append(item)
    return unique
