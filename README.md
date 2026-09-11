# 🎓 Chatbot RAG — FUNDEB, VAAR & ICMS Educacional (MG)

Chatbot com **RAG (Retrieval-Augmented Generation)** que responde perguntas
conceituais sobre FUNDEB, VAAR, ICMS Educacional, indicadores e legislação
de Minas Gerais, com base na documentação do projeto **Uai Sô**.

> Este é um projeto **novo e independente**. O repositório do Uai Sô é usado
> apenas como **fonte de regras e documentação** (README, fórmulas,
> legislação) para alimentar a base de conhecimento do RAG — o chatbot não
> reutiliza nem depende do código do Uai Sô em tempo de execução.

## Índice

- [Arquitetura](#arquitetura)
- [Justificativa das escolhas de stack](#justificativa-das-escolhas-de-stack)
- [Como rodar](#como-rodar)
- [Custo estimado](#custo-estimado)
- [Latência estimada](#latência-estimada)
- [Método de avaliação](#método-de-avaliação)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Limitações e próximos passos](#limitações-e-próximos-passos)

## Arquitetura

```
Usuário
   │
   ▼
Streamlit (app.py) ── interface de chat, histórico, loading, erros
   │
   ▼
ChatService (src/chat) ── orquestra o caso de uso "responder pergunta"
   │
   ├──► EmbeddingModel (SentenceTransformer, local) ─┐
   │                                                  │
   ├──► VectorStore (ChromaDB, local/persistente) ◄───┘  recuperação semântica
   │        gerado 1x por: python -m src.ingestion.build_index
   │        a partir de data/source_docs/ (README, regras de negócio, legislação)
   │
   └──► LLMClient (Groq API, padrão | Ollama, alternativa local)
            gera a resposta final com base apenas no contexto recuperado
```

Princípios seguidos:

- **Ports & Adapters (DDD leve)**: `src/domain/ports.py` define os
  contratos (`EmbeddingModel`, `VectorStore`, `LLMClient`); as
  implementações concretas (Chroma, sentence-transformers, Groq, Ollama)
  vivem em módulos separados e são plugadas via `src/chat/factory.py`.
  Trocar Groq por Ollama, ou Chroma por outro banco vetorial, não exige
  tocar em `chat_service.py` nem em `app.py`.
- **Ingestão separada da consulta**: `src/ingestion/build_index.py` roda
  uma única vez (ou sempre que a documentação mudar) e persiste os
  embeddings em disco (`data/chroma_db/`). O chat nunca reprocessa os
  documentos a cada pergunta.
- **Sem alucinação de cálculos**: o LLM nunca faz contas de repasse por
  município — o prompt de sistema o instrui a redirecionar esse tipo de
  pergunta para a calculadora do Uai Sô, e a responder apenas com base no
  contexto recuperado, dizendo explicitamente quando não sabe.

## Justificativa das escolhas de stack

| Decisão | Escolha | Por quê |
|---|---|---|
| LLM | **Groq API** (`openai/gpt-oss-120b`) | Inference em hardware próprio (LPU) com centenas de tokens/s — latência muito baixa; tier gratuito sem cartão de crédito; preço por token entre os mais baixos do mercado (US$0,15/US$0,60 por milhão de tokens). `openai/gpt-oss-20b` é uma alternativa ainda mais rápida e barata (US$0,075/US$0,30 por milhão), caso a velocidade importe mais que a qualidade da resposta. Alternativa local via **Ollama** já implementada atrás da mesma interface (`LLMClient`), bastando trocar `LLM_PROVIDER=ollama` no `.env` — útil se não houver internet ou se quiser custo zero mesmo no free tier. |
| Embeddings | `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), local | Modelo leve (~120 MB), multilíngue (essencial para PT-BR), roda em CPU em milissegundos e sem custo por chamada — evita pagar por embeddings a cada ingestão. |
| Banco vetorial | **ChromaDB** (persistência local em arquivo) | Embarcado, sem servidor externo, gratuito, simples de configurar — adequado ao volume pequeno/médio de documentos deste projeto e ao requisito de deploy local. |
| Interface | **Streamlit** | Interface web mínima, mesma tecnologia do projeto Uai Sô, permite construir um chat funcional (histórico, loading, tratamento de erro) em poucas linhas. |
| Arquitetura | DDD leve (ports & adapters) + Clean Code | Mantém RAG, geração de texto e interface desacoplados, o que facilita testes automatizados e a troca futura de provedor de LLM/embeddings sem retrabalho. |

## Como rodar

### 1. Pré-requisitos

- Python 3.10+
- Uma chave de API gratuita da Groq: crie em https://console.groq.com/keys
  (ou, alternativamente, o [Ollama](https://ollama.com) instalado e rodando
  localmente, caso prefira `LLM_PROVIDER=ollama`).

### 2. Instalação

```bash
git clone <URL_DESTE_REPOSITORIO>
cd chatbot-fundeb-icms-mg
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuração

```bash
cp .env.example .env
# edite o .env e cole sua GROQ_API_KEY
```

### 4. Construir o índice (ingestão) — rodar 1x, ou sempre que atualizar os docs

```bash
python -m src.ingestion.build_index
```

Isso lê tudo em `data/source_docs/`, divide em chunks, gera embeddings
localmente e persiste no ChromaDB (`data/chroma_db/`).

### 5. Rodar a aplicação

```bash
streamlit run app.py
```

Acesse `http://localhost:8501`.

### 6. (Opcional) Rodar a avaliação automatizada

```bash
python -m tests.eval_qa
```

## Custo estimado

Com o Groq (`openai/gpt-oss-120b`, US$0,15 / US$0,60 por milhão de
tokens de entrada/saída):

- Uma interação típica (pergunta + ~4 trechos de contexto + resposta) usa
  aproximadamente 600–1.000 tokens de entrada e 150–300 de saída.
- Custo por pergunta: **≈ US$0,0002–0,0003** (uma fração de centavo de
  dólar) — confirmado na prática pelo `tests/eval_qa.py`, que mediu
  ≈US$0,0002 para um lote de 6 perguntas.
- O tier gratuito da Groq (sem cartão) já cobre um volume alto de perguntas
  para fins de demonstração e uso pessoal, sem custo algum.
- Os embeddings (sentence-transformers) rodam localmente e têm **custo
  zero**, independentemente do volume de perguntas.
- Usando `LLM_PROVIDER=ollama`, o custo de inferência também é zero
  (limitado apenas pelo hardware local).

## Latência estimada

- **Recuperação (embeddings + busca no Chroma)**: tipicamente < 100ms em
  CPU comum, para a base documental atual (poucas dezenas de chunks).
- **Geração (Groq, `openai/gpt-oss-120b`)**: ~1–2 segundos para uma
  resposta de 150–300 tokens, dado o throughput de centenas de tokens/s da
  Groq. Medido na prática: latência média de ≈1,3s por pergunta no
  `tests/eval_qa.py`.
- **Latência total por pergunta**: tipicamente entre 1 e 3 segundos.
- Com Ollama local, a latência passa a depender do hardware disponível
  (pode ser mais lenta em máquinas sem GPU).

## Método de avaliação

O arquivo `tests/eval_qa.py` define um pequeno conjunto de perguntas-gabarito
("golden set") cobrindo fórmulas, legislação, condicionalidades e
funcionamento do sistema — incluindo uma pergunta propositalmente fora do
escopo, para verificar se o chatbot **recusa responder** quando não há
contexto suficiente (evitando alucinação).

Para cada pergunta, o script mede:

1. **Assertividade** — se a resposta contém pelo menos uma palavra-chave
   esperada **e** cita a fonte correta.
2. **Latência** — tempo de resposta ponta a ponta.
3. **Custo estimado** — tokens aproximados × preço do modelo configurado.

Isso complementa os testes unitários em `tests/` (que usam dublês das
portas do domínio, sem depender de rede ou de modelos reais, e cobrem o
chunker, o carregador de documentos, os templates de prompt e a lógica de
orquestração do `ChatService`).

Já `tests/debug_retrieval.py` isola só a recuperação (sem chamar o LLM):
mostra, para um conjunto de perguntas, todos os chunks candidatos com seu
score de similaridade bruto, sem aplicar o limiar `RAG_MIN_SCORE`. Foi essa
ferramenta que revelou um bug real no chunker (títulos curtos seguidos de
tabelas longas geravam dezenas de chunks quase idênticos, que dominavam o
`top_k` e escondiam os trechos corretos) — corrigido, o que elevou a
assertividade do golden set de 33% para 100%.

```bash
# Testes unitários (rápidos, sem rede)
pytest tests/ -v

# Diagnóstico de recuperação (scores brutos, sem LLM)
python -m tests.debug_retrieval

# Avaliação fim-a-fim (requer índice construído e API configurada)
python -m tests.eval_qa
```

## Estrutura do projeto

```
chatbot-fundeb-icms-mg/
├── app.py                        # Interface Streamlit (chat)
├── requirements.txt
├── .env.example
├── src/
│   ├── domain/
│   │   ├── entities.py           # ChatMessage, DocumentChunk, ChatAnswer, Source
│   │   └── ports.py              # Contratos: EmbeddingModel, VectorStore, LLMClient
│   ├── config/
│   │   └── settings.py           # Configuração via .env
│   ├── ingestion/
│   │   ├── document_loader.py    # Lê data/source_docs/
│   │   ├── chunker.py            # Divisão em chunks (função pura)
│   │   ├── embedder.py           # Adapter: sentence-transformers
│   │   └── build_index.py        # Pipeline de ingestão (CLI)
│   ├── retrieval/
│   │   └── chroma_store.py       # Adapter: ChromaDB
│   ├── generation/
│   │   ├── prompt_templates.py   # System prompt + montagem do contexto
│   │   ├── groq_client.py        # Adapter: Groq API
│   │   └── ollama_client.py      # Adapter: Ollama local
│   └── chat/
│       ├── chat_service.py       # Caso de uso: responder pergunta via RAG
│       └── factory.py            # Composition root (monta os adapters)
├── data/
│   ├── source_docs/               # Base de conhecimento (Markdown)
│   │   ├── uaiso_readme.md
│   │   ├── uaiso_continuacao.md
│   │   ├── regras_negocio.md
│   │   └── legislacao/
│   └── chroma_db/                 # Índice vetorial persistido
└── tests/
    ├── test_chunker.py
    ├── test_document_loader.py
    ├── test_prompt_templates.py
    ├── test_chat_service.py
    ├── debug_retrieval.py         # Diagnóstico de recuperação (scores brutos)
    └── eval_qa.py                 # Avaliação fim-a-fim (golden set)
```

## Limitações e próximos passos

- A Groq descontinua modelos com alguma frequência (ex.: `llama-3.3-70b-versatile`
  foi desativado em ago/2026). Se `GROQ_MODEL` retornar erro 404
  `model_not_found`, confira a lista atual em
  [console.groq.com/docs/models](https://console.groq.com/docs/models) e
  atualize a variável no `.env` — o código não precisa mudar.
- A base de conhecimento atual cobre README, notas de continuação e regras
  de negócio extraídas do código do Uai Sô. Para aprofundar respostas
  sobre a legislação, recomenda-se adicionar o texto oficial das normas
  (EC 108/2020, Lei 14.113/2020, Lei 18.030/2009, Lei 24.431/2023) em
  `data/source_docs/legislacao/` e reexecutar a ingestão.
- O chatbot **não** executa cálculos de repasse por município — isso
  permanece na calculadora determinística do Uai Sô, por design.
- Não há autenticação nem persistência de conversas entre sessões
  (fora de escopo para esta entrega mínima).