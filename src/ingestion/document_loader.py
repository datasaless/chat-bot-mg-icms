"""
src/ingestion/document_loader.py
Lê os documentos-fonte (Markdown/texto) que compõem a base de conhecimento
do RAG. Não sabe nada sobre chunking, embeddings ou banco vetorial.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass(frozen=True)
class RawDocument:
    title: str
    path: str
    text: str


def load_documents(source_dir: Path) -> list[RawDocument]:
    """Carrega recursivamente todos os documentos suportados de source_dir."""
    documents: list[RawDocument] = []

    for file_path in sorted(source_dir.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            text = file_path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            documents.append(
                RawDocument(
                    title=_derive_title(file_path, text),
                    path=str(file_path.relative_to(source_dir)),
                    text=text,
                )
            )
    return documents


def _derive_title(file_path: Path, text: str) -> str:
    """Usa o primeiro cabeçalho Markdown como título, ou o nome do arquivo."""
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if line.strip().startswith("#") and stripped:
            return stripped
    return file_path.stem.replace("_", " ").title()
