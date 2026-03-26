import asyncio
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import streamlit as st
from src.core.workflow import Chat
from  st_module import login_popup
from src.core.db import PGManager

domains = ['Society & Culture',
 'Science & Mathematics',
 'Health',
 'Education & Reference',
 'Computers & Internet',
 'Sports',
 'Business & Finance',
 'Entertainment & Music',
 'Family & Relationships',
 'Politics & Government']
chat = Chat()
db = PGManager(
    dbname="DecisionMaker",
    host="localhost",
    user="postgres",
    password="postgres"
)
st.sidebar.title("Navigation Bar")
st.sidebar.selectbox(
    label="Navigate to Desired Page",
    options=["Chat", "My Profile"]
)    
st.title("Decision Maker AI Application")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    login_popup(db=db)

domain = st.selectbox(label="Select a preset", options=domains, placeholder="")


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
        "domain": domain,
        "instructions": [],
        "messages": [],
        #"counter": 0,
        "score": 0,
        "corrections": "",
        "final_reponse": "",
        "context": context
    }))
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content":response})
