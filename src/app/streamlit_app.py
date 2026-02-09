import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import numpy as np
from src.graph.workflow import build_chat_graph
from src.utils import load_presets, load_team

presets = load_presets()
chat = build_chat_graph()

st.title("Decision Maker AI Application")
preset = st.selectbox(label="Select a preset", options=presets.keys(), placeholder="")
team = load_team(preset_name=preset)

if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input(placeholder="Your message"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    response = chat.invoke({
        "question": query,
        "team": team,
        "instructions": [],
        "aggregated_messaages": [],
        "final_reponse": ""
    })["final_response"].content.replace("$", "\$")
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
