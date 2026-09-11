"""
src/generation/ollama_client.py
Implementação de LLMClient usando um servidor Ollama local.

Alternativa 100% local e sem custo por token à Groq — útil quando não se
quer depender de uma API externa. Trade-off: latência e qualidade dependem
do hardware local (CPU/GPU disponível) e do modelo baixado.
"""
from __future__ import annotations

import requests

from src.domain.entities import ChatMessage, Role
from src.domain.ports import LLMClient


class OllamaLLMClient(LLMClient):
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def complete(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        payload_messages = [{"role": "system", "content": system_prompt}]
        payload_messages += [
            {"role": _map_role(m.role), "content": m.content} for m in messages
        ]

        response = requests.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": payload_messages,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


def _map_role(role: Role) -> str:
    return "assistant" if role == Role.ASSISTANT else "user"
