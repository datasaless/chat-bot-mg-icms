"""
src/ingestion/build_index.py
Pipeline de ingestão: lê os documentos-fonte, divide em chunks, gera
embeddings e persiste no banco vetorial (Chroma).

Roda separadamente da aplicação de chat (`python -m src.ingestion.build_index`),
para que os documentos não precisem ser reprocessados a cada pergunta do
usuário. Deve ser executado sempre que a base documental for atualizada.
"""
from __future__ import annotations

import hashlib
import sys

from src.config.settings import CHROMA_DB_DIR, SOURCE_DOCS_DIR, settings
from src.domain.entities import DocumentChunk
from src.ingestion.chunker import chunk_text
from src.ingestion.document_loader import load_documents
from src.ingestion.embedder import SentenceTransformerEmbedder
from src.retrieval.chroma_store import ChromaVectorStore


def _chunk_id(source_path: str, index: int) -> str:
    digest = hashlib.sha1(f"{source_path}:{index}".encode("utf-8")).hexdigest()[:12]
    return f"{digest}"


def build_index() -> int:
    print(f"Lendo documentos de: {SOURCE_DOCS_DIR}")
    documents = load_documents(SOURCE_DOCS_DIR)

    if not documents:
        print("Nenhum documento encontrado em data/source_docs. Nada a indexar.")
        return 0

    print(f"{len(documents)} documento(s) encontrado(s). Dividindo em chunks...")
    all_chunks: list[DocumentChunk] = []
    for doc in documents:
        pieces = chunk_text(doc.text, settings.chunk_size, settings.chunk_overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append(
                DocumentChunk(
                    id=_chunk_id(doc.path, i),
                    text=piece,
                    source_title=doc.title,
                    source_path=doc.path,
                )
            )
        print(f"  - {doc.path}: {len(pieces)} chunk(s)")

    print(f"Total de {len(all_chunks)} chunks. Gerando embeddings "
          f"({settings.embedding_model_name})...")
    embedder = SentenceTransformerEmbedder(settings.embedding_model_name)
    embeddings = embedder.embed([chunk.text for chunk in all_chunks])

    print(f"Persistindo no banco vetorial em: {CHROMA_DB_DIR}")
    store = ChromaVectorStore(CHROMA_DB_DIR, settings.collection_name)
    store.upsert(all_chunks, embeddings)

    print("Índice construído com sucesso.")
    return len(all_chunks)


if __name__ == "__main__":
    count = build_index()
    sys.exit(0 if count >= 0 else 1)
