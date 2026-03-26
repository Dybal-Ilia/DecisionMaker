import streamlit as st
from src.core.schemas import User
from uuid import uuid4
import hashlib

st.cache_data(ttl=3600)
def get_nicknames_list(_db):
    sql = """
            SELECT 
                user_nickname
            FROM public.users
            """
    _db.cursor.execute(sql)
    res = _db.cursor.fetchall()
    nickname_list = [r[0] for r in res]
    return nickname_list


def check_login(db, user_nickname, user_password):
    all_nicknames = get_nicknames_list(db)

    if not user_nickname in all_nicknames:
        return False
    sql = f"""SELECT 
                user_password
             FROM public.users WHERE user_nickname = '{user_nickname}'
                """
    db.cursor.execute(sql)
    db_password_hash = db.cursor.fetchone()[0]
    user_password_hash = hashlib.sha256(user_password.encode("utf-8")).hexdigest()
    return db_password_hash == user_password_hash



def check_password_strong(user_password):
    if len(user_password) < 8:
        return False
    return True

@st.dialog("Welcome! Please Log In or Sign Up", dismissible=False)
def login_popup(db):
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
    with tab_login:
        user_nickname = st.text_input(label="Your Nickname", key="login nickname")
        user_password = st.text_input(label="Your Password", type="password", key="login password")
        if st.button("Log In", use_container_width=True):
            login_result = check_login(db, user_nickname, user_password)
            if login_result:
                st.success("Successfully Logged In")
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect Nickname or Password")
    with tab_signup:
        user_name = st.text_input("Your First Name", key="signup name")
        user_lastname = st.text_input("Your Last Name", key="signup lastname")
        user_nickname = st.text_input("Your Nickname", key="signup nickname")
        user_password = st.text_input("Your Password", type="password", key="signup password")
        if st.button("Sign Up"):
            is_password_strong = check_password_strong(user_password)
            if not is_password_strong:
                st.error("Password isn't strong enough. It should be at least 8 charachters long")
            else:
                user_id = uuid4()
                user_password_hash = hashlib.sha256(user_password.encode("utf-8")).hexdigest()
                user = User(
                    user_id=user_id,
                    user_name=user_name,
                    user_lastname=user_lastname,
                    user_nickname=user_nickname,
                    user_password=user_password_hash
                )
                create_user_status = db.create_user(user)
                if create_user_status:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Sign Up went wrong. Please try again")