"""
src/generation/groq_client.py
Implementação de LLMClient usando a API da Groq.

Escolha de stack: a Groq roda modelos open-source (Llama 3.x) em hardware
próprio (LPU), entregando latência muito baixa (centenas de tokens/segundo)
a um custo por token muito inferior ao de provedores tradicionais, e possui
tier gratuito sem cartão de crédito — adequado para um projeto acadêmico.
"""
from __future__ import annotations

from groq import Groq

from src.domain.entities import ChatMessage, Role
from src.domain.ports import LLMClient


class GroqLLMClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY não configurada. Defina a variável de ambiente "
                "ou crie um arquivo .env a partir do .env.example."
            )
        self._client = Groq(api_key=api_key)
        self._model = model

    def complete(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        payload = [{"role": "system", "content": system_prompt}]
        payload += [{"role": _map_role(m.role), "content": m.content} for m in messages]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=payload,
            temperature=0.2,
            max_tokens=800,
        )
        return response.choices[0].message.content


def _map_role(role: Role) -> str:
    return "assistant" if role == Role.ASSISTANT else "user"
