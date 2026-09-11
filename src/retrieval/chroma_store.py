"""
src/retrieval/chroma_store.py
Implementação concreta de VectorStore usando ChromaDB com persistência local
em disco (data/chroma_db). Escolhido por: roda embarcado (sem servidor
separado), gratuito, e suficiente para uma base documental pequena/média
como a deste projeto.
"""
from __future__ import annotations

from pathlib import Path

import chromadb

from src.domain.entities import DocumentChunk, RetrievedChunk
from src.domain.ports import VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: Path, collection_name: str) -> None:
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def upsert(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {"source_title": chunk.source_title, "source_path": chunk.source_path}
                for chunk in chunks
            ],
        )

    def query(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        if self.is_empty():
            return []

        result = self._collection.query(query_embeddings=[embedding], n_results=top_k)

        retrieved: list[RetrievedChunk] = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            chunk = DocumentChunk(
                id=chunk_id,
                text=document,
                source_title=metadata.get("source_title", "Desconhecido"),
                source_path=metadata.get("source_path", ""),
            )
            # Chroma retorna distância (quanto menor, mais similar); convertemos
            # para um score de similaridade no intervalo aproximado [0, 1].
            score = 1.0 / (1.0 + distance)
            retrieved.append(RetrievedChunk(chunk=chunk, score=score))

        return retrieved

    def is_empty(self) -> bool:
        return self._collection.count() == 0
