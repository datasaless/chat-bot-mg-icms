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
    # Uma fronteira de parágrafo/frase só é aceita se o chunk resultante tiver
    # pelo menos essa fração de chunk_size — evita cortes minúsculos logo no
    # início de uma seção curta (ex.: "## Título\n\n" seguido de uma tabela
    # longa sem outra quebra de parágrafo por perto).
    min_chunk_len = max(1, int(chunk_size * 0.5))

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            boundary = _find_boundary(text, start, end, min_chunk_len)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        # Sobreposição só é aplicada se ainda garantir avanço real do cursor;
        # senão (chunk pequeno, overlap grande) avança sem sobreposição, para
        # nunca ficar "preso" avançando poucos caracteres por iteração.
        next_start = end - overlap
        start = next_start if next_start > start else end

    return chunks


def _find_boundary(text: str, start: int, end: int, min_chunk_len: int) -> int:
    """Procura a última quebra de parágrafo, ou de frase, dentro de [start, end),
    aceitando apenas fronteiras que produzam um chunk de tamanho mínimo."""
    window = text[start:end]

    for separator in ("\n\n", ". ", "\n"):
        idx = window.rfind(separator)
        if idx != -1 and idx >= min_chunk_len:
            return start + idx + len(separator)

    return end