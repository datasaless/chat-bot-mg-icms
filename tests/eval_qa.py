"""
tests/eval_qa.py
Método de avaliação do chatbot: um pequeno conjunto de perguntas-gabarito
(golden set) com palavras-chave esperadas na resposta e a fonte esperada.

Diferente dos testes unitários (que usam dublês), este script chama o
pipeline real (embeddings locais + Groq/Ollama) e por isso requer o índice
já construído e as credenciais configuradas no .env.

Uso:
    python -m tests.eval_qa

Para cada pergunta, mede:
  - Assertividade: se ao menos uma palavra-chave esperada aparece na
    resposta E se a fonte esperada foi citada.
  - Latência: tempo de resposta (segundos).
  - Custo estimado: tokens aproximados (chars / 4) x preço do modelo
    configurado, apenas como referência de ordem de grandeza.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from src.chat.factory import build_chat_service
from src.config.settings import settings

# Preço aproximado por 1M tokens (USD) — apenas referência, atualizar conforme
# a tabela de preços vigente da Groq (console.groq.com/docs/models).
PRECO_POR_1M_TOKENS = {
    "openai/gpt-oss-120b": {"input": 0.15, "output": 0.60},
    "openai/gpt-oss-20b": {"input": 0.075, "output": 0.30},
}


@dataclass
class CasoTeste:
    pergunta: str
    palavras_chave: list[str]
    fontes_esperadas: tuple[str, ...] = ()  # aceita qualquer uma das fontes listadas


CASOS_TESTE = [
    CasoTeste(
        pergunta="Qual é a fórmula do IQE?",
        palavras_chave=["IRAP", "0,50", "0.50"],
        fontes_esperadas=("regras_negocio.md",),
    ),
    CasoTeste(
        pergunta="O que é o VAAR?",
        palavras_chave=["FUNDEB", "complementação"],
        fontes_esperadas=("regras_negocio.md",),
    ),
    CasoTeste(
        pergunta="Quais são as condicionalidades para um município receber o VAAR?",
        palavras_chave=["SAEB", "BNCC", "80%"],
        fontes_esperadas=("regras_negocio.md",),
    ),
    CasoTeste(
        pergunta="Quais leis fundamentam o ICMS Educacional em Minas Gerais?",
        palavras_chave=["24.431", "18.030"],
        fontes_esperadas=("regras_negocio.md",),
    ),
    CasoTeste(
        pergunta="Quais páginas o sistema Uai Sô oferece?",
        palavras_chave=["Calculadora", "Mapa", "Ranking"],
        # README e CONTINUACAO têm listas de páginas equivalentes — qualquer
        # um dos dois como fonte é uma resposta correta.
        fontes_esperadas=("uaiso_readme.md", "uaiso_continuacao.md"),
    ),
    CasoTeste(
        pergunta="Qual é a capital da Mongólia?",
        palavras_chave=["não encontr", "não há", "não tenho"],
        fontes_esperadas=(),  # espera-se que o bot recuse por falta de contexto
    ),
]


def run() -> None:
    service = build_chat_service()

    acertos = 0
    latencias: list[float] = []
    tokens_estimados_total = 0

    for caso in CASOS_TESTE:
        inicio = time.perf_counter()
        resposta = service.ask(caso.pergunta)
        duracao = time.perf_counter() - inicio
        latencias.append(duracao)

        texto_lower = resposta.text.lower()
        tem_palavra_chave = any(p.lower() in texto_lower for p in caso.palavras_chave)
        tem_fonte = not caso.fontes_esperadas or any(
            fe in s.path for fe in caso.fontes_esperadas for s in resposta.sources
        )
        passou = tem_palavra_chave and tem_fonte
        acertos += int(passou)

        tokens_estimados_total += (len(caso.pergunta) + len(resposta.text)) // 4

        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{status} | {duracao:.2f}s | {caso.pergunta}")
        if resposta.sources:
            fontes_str = ", ".join(
                f"{s.path}({s.relevance_score:.2f})" for s in resposta.sources
            )
            print(f"   fontes: {fontes_str}")
        if not passou:
            print(f"   resposta: {resposta.text[:200]}")

    total = len(CASOS_TESTE)
    assertividade = acertos / total * 100
    latencia_media = sum(latencias) / len(latencias)

    preco = PRECO_POR_1M_TOKENS.get(settings.groq_model, {"input": 0, "output": 0})
    custo_estimado = tokens_estimados_total / 1_000_000 * (preco["input"] + preco["output"]) / 2

    print("\n--- Resumo da avaliação ---")
    print(f"Assertividade: {acertos}/{total} ({assertividade:.1f}%)")
    print(f"Latência média: {latencia_media:.2f}s")
    print(f"Tokens estimados no lote: ~{tokens_estimados_total}")
    print(f"Custo estimado do lote: ~US$ {custo_estimado:.5f} (modelo: {settings.groq_model})")


if __name__ == "__main__":
    run()