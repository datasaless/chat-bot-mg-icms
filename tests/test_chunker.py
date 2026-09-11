import pytest

from src.ingestion.chunker import chunk_text


def test_texto_curto_retorna_um_unico_chunk():
    text = "Texto pequeno que cabe em um único chunk."
    result = chunk_text(text, chunk_size=100, overlap=10)
    assert result == [text]


def test_texto_vazio_retorna_lista_vazia():
    assert chunk_text("   ", chunk_size=100, overlap=10) == []


def test_texto_longo_gera_multiplos_chunks_com_tamanho_respeitado():
    text = "Palavra " * 500  # ~4000 caracteres
    chunks = chunk_text(text, chunk_size=800, overlap=100)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 800 + 50  # margem para ajuste de fronteira


def test_chunks_consecutivos_tem_sobreposicao():
    text = "frase um. frase dois. frase tres. " * 50
    chunks = chunk_text(text, chunk_size=200, overlap=50)

    assert len(chunks) > 1
    # A sobreposição garante que o fim de um chunk reaparece no início do próximo
    for prev, nxt in zip(chunks, chunks[1:]):
        assert any(word in nxt[:80] for word in prev[-30:].split())


@pytest.mark.parametrize("chunk_size,overlap", [(0, 0), (-10, 0), (100, 100), (100, 150)])
def test_parametros_invalidos_levantam_erro(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("qualquer texto", chunk_size=chunk_size, overlap=overlap)
