from src.chat.chat_service import ChatService
from src.domain.entities import DocumentChunk, RetrievedChunk


class FakeEmbedder:
    def embed(self, texts):
        return [[1.0, 0.0] for _ in texts]


class FakeVectorStoreEmpty:
    def upsert(self, chunks, embeddings):
        pass

    def query(self, embedding, top_k):
        return []

    def is_empty(self):
        return True


class FakeVectorStoreWithData:
    def __init__(self, chunks_and_scores):
        self._data = chunks_and_scores

    def upsert(self, chunks, embeddings):
        pass

    def query(self, embedding, top_k):
        return self._data[:top_k]

    def is_empty(self):
        return False


class FakeLLM:
    def __init__(self, response="resposta simulada"):
        self.response = response
        self.last_messages = None

    def complete(self, system_prompt, messages):
        self.last_messages = messages
        return self.response


def _make_chunk(path="doc.md", title="Documento", text="Conteúdo relevante"):
    return DocumentChunk(id="1", text=text, source_title=title, source_path=path)


def test_avisa_quando_base_de_conhecimento_esta_vazia():
    service = ChatService(FakeEmbedder(), FakeVectorStoreEmpty(), FakeLLM())

    answer = service.ask("O que é o VAAR?")

    assert "não foi indexada" in answer.text.lower() or "índice" in answer.text.lower()
    assert answer.sources == []
    assert answer.context_found is False


def test_retorna_resposta_e_fontes_quando_ha_contexto_relevante():
    retrieved = [RetrievedChunk(chunk=_make_chunk(), score=0.9)]
    llm = FakeLLM(response="O VAAR é a complementação do FUNDEB.")
    service = ChatService(FakeEmbedder(), FakeVectorStoreWithData(retrieved), llm)

    answer = service.ask("O que é o VAAR?")

    assert answer.text == "O VAAR é a complementação do FUNDEB."
    assert len(answer.sources) == 1
    assert answer.sources[0].title == "Documento"
    assert answer.context_found is True


def test_ignora_chunks_com_score_abaixo_do_minimo():
    retrieved = [RetrievedChunk(chunk=_make_chunk(), score=0.01)]
    service = ChatService(FakeEmbedder(), FakeVectorStoreWithData(retrieved), FakeLLM())

    answer = service.ask("Pergunta qualquer")

    assert answer.sources == []
    assert answer.context_found is False


def test_deduplica_fontes_repetidas():
    retrieved = [
        RetrievedChunk(chunk=_make_chunk(text="trecho 1"), score=0.9),
        RetrievedChunk(chunk=_make_chunk(text="trecho 2"), score=0.8),
    ]
    service = ChatService(FakeEmbedder(), FakeVectorStoreWithData(retrieved), FakeLLM())

    answer = service.ask("Pergunta qualquer")

    assert len(answer.sources) == 1
