import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import torch
import streamlit as st
from src.graph.workflow import Chat
from src.utils import load_presets, load_team
from transformers import AutoModelForSequenceClassification, AutoTokenizer

device = "cuda" if torch.cuda.is_available() else "cpu"

@st.cache_data
def load_tokenizer_and_model(model_ckpt:str):
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(model_ckpt).to(device)
    return tokenizer, model
tokenizer, model = load_tokenizer_and_model(model_ckpt="ilia-dybal/domain-classifier")

def predict_domain(tokenizer, model, query:str):
    id2label = {0: 'oos',
                1: 'banking',
                2: 'credit_cards',
                3: 'kitchen_and_dining',
                4: 'home',
                5: 'auto_and_commute',
                6: 'travel',
                7: 'utility',
                8: 'work',
                9: 'small_talk',
                10: 'meta'}
    inputs = tokenizer(query, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        predicted_id = outputs.logits.argmax(-1).item()
    label = id2label[predicted_id]
    return label

presets = load_presets()
chat = Chat(model_name="llama-3.1-8b-instant")

st.title("Decision Maker AI Application")
preset = st.selectbox(label="Select a preset", options=presets.keys(), placeholder="")
team = load_team(preset_name=preset)

input_text = st.text_input(label="Classifier Test")
st.write(predict_domain(tokenizer=tokenizer, model=model, query=input_text))



if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input(placeholder="Your message"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    response = chat.run_chat({
        "question": query,
        "team": team,
        "instructions": [],
        "aggregated_messaages": [],
        "final_reponse": ""
    })
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
