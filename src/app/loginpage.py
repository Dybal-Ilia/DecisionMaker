import streamlit as st
from st_module import check_login, check_password_strong, wrap_user, is_nickname_available
from src.core.db import get_db
import os
from dotenv import load_dotenv
load_dotenv()

DB_URI = os.getenv("DB_URI")

@st.dialog("Welcome! Please Log In or Sign Up", dismissible=False)
def render_login_popup():
    db = get_db(_db_uri=DB_URI)
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
    with tab_login:
        user_nickname = st.text_input(label="Your Nickname", key="login nickname")
        user_password = st.text_input(label="Your Password", type="password", key="login password")
        if st.button("Log In", use_container_width=True):
            login_result = check_login(db, user_nickname, user_password)
            if login_result:
                st.success("Successfully Logged In")
                st.session_state.logged_in = True
                st.session_state.logged_user_nickname = user_nickname
                st.toast(f"Successfully logged in as {user_nickname}")
                st.rerun()
            else:
                st.error("Incorrect Nickname or Password")
    with tab_signup:
        user_name = st.text_input("Your First Name", key="signup name")
        user_lastname = st.text_input("Your Last Name", key="signup lastname")
        user_nickname = st.text_input("Your Nickname", key="signup nickname")
        if user_nickname:
            nickname_available = is_nickname_available(db=db, nickname=user_nickname)
            if not nickname_available:
                st.error(f"Nickname '{user_nickname}' is already taken, please choose another one")
        user_password = st.text_input("Your Password", type="password", key="signup password")
        if st.button("Sign Up"):
            is_password_strong = check_password_strong(user_password)
            if not is_password_strong:
                st.error("Password isn't strong enough. It should be at least 8 charachters long")
            else:
                user = wrap_user(
                    user_name=user_name,
                    user_lastname=user_lastname,
                    user_nickname=user_nickname,
                    user_password=user_password 
                )
                create_user_status = db.loop.run_until_complete(db.create_user(user))
                if create_user_status:
                    st.session_state.logged_in = True
                    st.session_state.logged_user_nickname = user_nickname
                    st.rerun()
                else:
                    st.error("Sign Up went wrong. Please try again")