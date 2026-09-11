from src.domain.entities import DocumentChunk, RetrievedChunk
from src.generation.prompt_templates import build_context_block, build_user_prompt


def test_contexto_vazio_quando_sem_chunks():
    assert "nenhum trecho relevante" in build_context_block([]).lower()


def test_contexto_inclui_titulo_e_texto_dos_chunks():
    chunk = DocumentChunk(id="1", text="IQE = IRAP*0.5", source_title="Regras de Negócio",
                           source_path="regras_negocio.md")
    block = build_context_block([RetrievedChunk(chunk=chunk, score=0.9)])

    assert "Regras de Negócio" in block
    assert "IQE = IRAP*0.5" in block


def test_prompt_do_usuario_inclui_pergunta_e_contexto():
    chunk = DocumentChunk(id="1", text="conteúdo", source_title="Doc", source_path="doc.md")
    prompt = build_user_prompt("O que é o IQE?", [RetrievedChunk(chunk=chunk, score=0.9)])

    assert "O que é o IQE?" in prompt
    assert "conteúdo" in prompt
    assert "CONTEXTO" in prompt
