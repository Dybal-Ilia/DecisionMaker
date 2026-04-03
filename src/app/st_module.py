import streamlit as st
from src.core.schemas import User
from src.core.workflow import Drafter, Chat
from uuid import uuid4
import hashlib
import asyncio

@st.cache_resource
def get_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

@st.cache_resource
def get_drafter_agent():
    return Drafter()

@st.cache_resource
def get_chat_agent():
    return Chat()

def check_login(db, user_nickname, user_password):
    all_nicknames = db.loop.run_until_complete(db.get_nicknames_list())

    if all_nicknames is None or not user_nickname in all_nicknames:
        return False
        
    db_password_hash = db.loop.run_until_complete(db.fetch_password_by_nickname(user_nickname))
    if db_password_hash is None:
        return False
    user_password_hash = hashlib.sha256(user_password.encode("utf-8")).hexdigest()
    return db_password_hash == user_password_hash


def check_password_strong(user_password):
    if len(user_password) < 8:
        return False
    return True

def wrap_user(user_name:str,
              user_lastname:str,
              user_nickname:str,
              user_password:str):
    user_id = uuid4()
    user_password_hash = hashlib.sha256(user_password.encode("utf-8")).hexdigest()
    user = User(
                user_id=user_id,
                user_name=user_name,
                user_lastname=user_lastname,
                user_nickname=user_nickname,
                user_password=user_password_hash
                )
    return user

def is_nickname_available(db, nickname):
    all_nicknames = db.loop.run_until_complete(db.get_nicknames_list())
    if nickname in all_nicknames:
        return False
    return True