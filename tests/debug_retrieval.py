"""
tests/debug_retrieval.py
Ferramenta de diagnóstico: para cada pergunta do golden set, mostra os
top_k chunks recuperados com seus scores de similaridade, SEM aplicar
nenhum limiar (RAG_MIN_SCORE). Não chama o LLM — só embeddings + Chroma.

Uso:
    python -m tests.debug_retrieval
"""
from __future__ import annotations

from src.config.settings import CHROMA_DB_DIR, settings
from src.ingestion.embedder import SentenceTransformerEmbedder
from src.retrieval.chroma_store import ChromaVectorStore

PERGUNTAS = [
    "Qual é a fórmula do IQE?",
    "O que é o VAAR?",
    "Quais são as condicionalidades para um município receber o VAAR?",
    "Quais leis fundamentam o ICMS Educacional em Minas Gerais?",
    "Quais páginas o sistema Uai Sô oferece?",
    "Qual é a capital da Mongólia?",
]


def run() -> None:
    embedder = SentenceTransformerEmbedder(settings.embedding_model_name)
    store = ChromaVectorStore(CHROMA_DB_DIR, settings.collection_name)

    if store.is_empty():
        print("Índice vazio. Rode primeiro: python -m src.ingestion.build_index")
        return

    for pergunta in PERGUNTAS:
        print(f"\n=== {pergunta} ===")
        embedding = embedder.embed([pergunta])[0]
        retrieved = store.query(embedding, top_k=10)

        if not retrieved:
            print("  (nenhum chunk retornado pelo Chroma — índice vazio ou erro)")
            continue

        for item in retrieved:
            preview = item.chunk.text.strip().replace("\n", " ")[:100]
            print(f"  score={item.score:.3f} | {item.chunk.source_path} | {preview}...")

    print(f"\nLimiar atual configurado (RAG_MIN_SCORE): {settings.min_relevance_score}")
    print(f"top_k atual configurado (RAG_TOP_K): {settings.top_k}")


if __name__ == "__main__":
    run()