import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#import torch
import streamlit as st
from src.graph.workflow import Chat

# from transformers import AutoModelForSequenceClassification, AutoTokenizer

# device = "cuda" if torch.cuda.is_available() else "cpu"

# @st.cache_data
# def load_tokenizer_and_model(model_ckpt:str) -> tuple[AutoTokenizer, AutoModelForSequenceClassification]:
#     """
#     Loads pretrained tokenizer and model for domain classification
    
#     :param model_ckpt: pretrained model name fromm hf
#     :type model_ckpt: str
#     """

#     tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
#     model = AutoModelForSequenceClassification.from_pretrained(model_ckpt).to(device)
#     return tokenizer, model

# tokenizer, model = load_tokenizer_and_model(model_ckpt="ilia-dybal/domain-classifier")

# def predict_domain(tokenizer, model, query:str):
#     id2label = {0: 'oos',
#                 1: 'banking',
#                 2: 'credit_cards',
#                 3: 'kitchen_and_dining',
#                 4: 'home',
#                 5: 'auto_and_commute',
#                 6: 'travel',
#                 7: 'utility',
#                 8: 'work',
#                 9: 'small_talk',
#                 10: 'meta'}
#     inputs = tokenizer(query, return_tensors="pt").to(device)
#     with torch.no_grad():
#         outputs = model(**inputs)
#         predicted_id = outputs.logits.argmax(-1).item()
#     label = id2label[predicted_id]
#     return label

# presets = load_presets()

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
chat = Chat(model_name="llama-3.1-8b-instant")

st.title("Decision Maker AI Application")
domain = st.selectbox(label="Select a preset", options=domains, placeholder="")


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
        "domain": domain,
        "instructions": [],
        "final_reponse": ""
    })
    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content":response})
