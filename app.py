"""
app.py
Interface web mínima do chatbot (Streamlit): chat com histórico, indicador
de carregamento, tratamento de erros e exibição das fontes usadas em cada
resposta.

Ponto de entrada: `streamlit run app.py`
"""
from __future__ import annotations

import streamlit as st

from src.chat.factory import build_chat_service
from src.domain.entities import ChatMessage, Role

st.set_page_config(page_title="Chatbot Uai Sô — FUNDEB & ICMS Educacional", page_icon="🎓")

st.title("🎓 Chatbot — FUNDEB, VAAR & ICMS Educacional (MG)")
st.caption(
    "Tire dúvidas conceituais sobre fórmulas, legislação e funcionamento do "
    "sistema Uai Sô. Para cálculos de um município específico, use a "
    "calculadora do Uai Sô."
)


@st.cache_resource(show_spinner=False)
def get_chat_service():
    return build_chat_service()


if "history" not in st.session_state:
    st.session_state.history = []  # list[ChatMessage]

for message in st.session_state.history:
    with st.chat_message(message.role.value):
        st.markdown(message.content)

question = st.chat_input("Pergunte sobre FUNDEB, VAAR, ICMS Educacional...")

if question:
    st.session_state.history.append(ChatMessage(role=Role.USER, content=question))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            try:
                service = get_chat_service()
                answer = service.ask(question, st.session_state.history[:-1])
            except Exception as exc:  # noqa: BLE001 — mostramos qualquer falha ao usuário
                st.error(
                    "Não foi possível gerar uma resposta agora. Verifique se o "
                    "índice foi construído (`python -m src.ingestion.build_index`) "
                    "e se as credenciais do LLM estão configuradas no `.env`.\n\n"
                    f"Detalhe técnico: {exc}"
                )
                st.stop()

        st.markdown(answer.text)

        if answer.sources:
            with st.expander("📚 Fontes utilizadas"):
                for source in answer.sources:
                    st.markdown(f"**{source.title}** (`{source.path}`)")
                    st.caption(source.snippet)
        elif not answer.context_found:
            st.caption(
                "⚠️ Nenhum trecho suficientemente relevante foi encontrado na "
                "base de conhecimento para esta pergunta."
            )

    st.session_state.history.append(ChatMessage(role=Role.ASSISTANT, content=answer.text))
