"""
src/ingestion/chunker.py
Divide texto longo em pedaços (chunks) menores, com sobreposição, para
melhorar a granularidade da recuperação semântica.

Função pura — sem I/O, sem dependências externas — fácil de testar.
"""
from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """
    Divide `text` em pedaços de até `chunk_size` caracteres, com `overlap`
    caracteres de sobreposição entre pedaços consecutivos.

    Tenta quebrar em fronteiras de parágrafo/frase quando possível, evitando
    cortar uma palavra ao meio.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser positivo")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap deve ser >= 0 e menor que chunk_size")

    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            boundary = _find_boundary(text, start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        start = max(end - overlap, start + 1)

    return chunks


def _find_boundary(text: str, start: int, end: int) -> int:
    """Procura a última quebra de parágrafo, ou de frase, dentro de [start, end)."""
    window = text[start:end]

    for separator in ("\n\n", ". ", "\n"):
        idx = window.rfind(separator)
        if idx != -1 and idx > 0:
            return start + idx + len(separator)

    return end
