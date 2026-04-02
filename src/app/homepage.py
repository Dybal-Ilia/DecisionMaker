import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loginpage import render_login_popup
from chatpage import render_chat_page
from profilepage import render_profile_page
from decisionspage import render_decisionpage

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "logged_user_nickname" not in st.session_state:
     st.session_state.logged_user_nickname = None

if st.session_state.logged_in:
    if "chat" not in st.session_state:
        from src.core.workflow import Chat
        st.session_state.chat = Chat()


def render_homepage():
    st.title("Homepage")
    st.divider()
    st.markdown("## Hi, there! Here's the manual how to use the app")
    st.markdown("### 1. Sign In or Sign Up")
    st.markdown("To start utilizing the app you need to create an account. To do so you should click *Sign In* link in the navigation bar." \
    "You will be offered 2 options: *Sign In* or *Sign Up*. Use *Sign In* in case you already have an account. Use *Sign Up* in case you don't have one." \
    "Once the account is created you will be **automatically** signed in", text_alignment="justify")
    st.divider()
    st.markdown("### 2. Start Chatting")
    st.markdown("Once you signed in, you will be given access to chat section. To start chatting use *Chat* link in the navigation bar.")
    st.divider()
    st.markdown("### 3. My Profile")
    st.markdown("You can also inspect your account. To do so click *My Profile* link in the navigation bar. There you will be able to see your personal data" \
    "like *First Name*, *Second Name* or *Nickname*. For now the information is not editable, but later in future you'll be able to edit your personal data", text_alignment="justify")
    st.divider()
    st.markdown("### 4. Analytics")
    st.markdown("In this section you will be able to inspect some dashboards like *Messages Sent*, *Tokens Used*, *Memories Saved*", text_alignment="justify")


home_page = st.Page(page=render_homepage, title="Home")
chat_page = st.Page(page=render_chat_page, title="Chat")
profile_page = st.Page(page=render_profile_page, title="My Profile")
login_page = st.Page(page=render_login_popup, title="Log In")
decision_page = st.Page(page=render_decisionpage, title="My Decisions")


if st.session_state.logged_in:
    pg = st.navigation([home_page, chat_page, profile_page, decision_page])
else:
    pg = st.navigation([home_page, login_page])
pg.run()