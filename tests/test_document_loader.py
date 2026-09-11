from src.ingestion.document_loader import load_documents


def test_carrega_documentos_markdown_e_extrai_titulo(tmp_path):
    (tmp_path / "a.md").write_text("# Título do Documento A\n\nConteúdo A.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Conteúdo sem cabeçalho.", encoding="utf-8")
    (tmp_path / "ignorar.png").write_bytes(b"\x89PNG")

    docs = load_documents(tmp_path)

    assert len(docs) == 2
    titles = {doc.title for doc in docs}
    assert "Título do Documento A" in titles
    assert "B" in titles  # fallback: nome do arquivo


def test_ignora_arquivos_vazios(tmp_path):
    (tmp_path / "vazio.md").write_text("   ", encoding="utf-8")
    docs = load_documents(tmp_path)
    assert docs == []
