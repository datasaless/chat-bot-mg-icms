"""
src/ingestion/embedder.py
Implementação concreta de EmbeddingModel usando sentence-transformers.

Escolha de stack: modelo multilíngue leve (~120MB), roda em CPU em
milissegundos por chunk, sem custo de API e sem depender de internet após
o primeiro download do modelo. Isso mantém o custo de embeddings em zero.
"""
from __future__ import annotations

from sentence_transformers import SentenceTransformer

from src.domain.ports import EmbeddingModel


class SentenceTransformerEmbedder(EmbeddingModel):
    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()
