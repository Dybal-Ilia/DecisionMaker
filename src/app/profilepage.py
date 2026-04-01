import streamlit as st
from src.core.db import get_db
import os
from dotenv import load_dotenv
load_dotenv()

DB_URI = os.getenv("DB_URI")

def render_profile_page():
    db = get_db(DB_URI)
    logged_user_nickname = st.session_state.logged_user_nickname
    first_name, last_name, nickname = db.loop.run_until_complete(db.get_user_by_nickname(logged_user_nickname))
    st.title("My Profile")
    st.write("")
    
    col1, col2 = st.columns([1, 4]) 
    
    with col1:
        initials = f"{first_name[0]}{last_name[0]}".upper()
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #6B73FF 10%, #000DFF 100%);
                color: white;
                border-radius: 50%;
                width: 100px;
                height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 38px;
                font-weight: bold;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            ">
                {initials}
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.header(f"{first_name} {last_name}")
        st.markdown(f"<h4 style='color: gray; margin-top: -15px;'>@{nickname}</h4>", unsafe_allow_html=True)
        st.caption("🟢 Active Account")
        
    st.divider()
    
    st.subheader("Account Details")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("**First Name**")
        st.write(first_name)
        st.write("")
        st.markdown("**Nickname**")
        st.write(nickname)
        
    with info_col2:
        st.markdown("**Last Name**")
        st.write(last_name)
        st.write("")
        st.markdown("**User ID**")
        st.caption("Hidden for security")
        
    st.divider()
    
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
    
    with btn_col1:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.toast("Edit feature coming soon!")
    with btn_col2:
        if st.button("🚪 Log Out", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()