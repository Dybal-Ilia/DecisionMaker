import streamlit as st
import asyncio

def render_chat_page():
    st.title("Decision Maker AI Application")
    # domains = ['Society & Culture',
    # 'Science & Mathematics',
    # 'Health',
    # 'Education & Reference',
    # 'Computers & Internet',
    # 'Sports',
    # 'Business & Finance',
    # 'Entertainment & Music',
    # 'Family & Relationships',
    # 'Politics & Government']
    chat = st.session_state.chat
    # domain = st.selectbox(label="Select a preset", options=domains, placeholder="")
    if "messages" not in st.session_state:
        st.session_state.messages= []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input(placeholder="Your message"):
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        context = ""
        for message in reversed(st.session_state.messages):
            if message["role"] == "assistant":
                context = message["content"]
                break
        response = asyncio.run(chat.run_chat({
            "question": query,
            "domain": "",
            "instructions": [],
            "messages": [],
            "counter": 0,
            # "score": 0,
            "corrections": "",
            "final_reponse": "",
            "context": context
        }))
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content":response})
