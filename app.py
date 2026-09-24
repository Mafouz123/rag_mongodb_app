import streamlit as st

from rag import query_data


st.set_page_config(
    page_title="Assistant RAG MongoDB",
    page_icon="📚",
)

st.title("Assistant documentaire")
st.write("Posez une question sur le document indexé dans MongoDB Atlas.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Votre question sur le document")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Recherche dans le document..."):
            try:
                answer = query_data(question)
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as error:
                st.error(f"Erreur pendant la recherche : {error}")