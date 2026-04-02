import streamlit as st


def render_decisionpage():
    st.header("Make a Decision")
    st.subheader("Here's how we help you make decisions. Please, fill in all the fields and our AI will help you analyze and choose the best one")
    st.divider()
    with st.container(border=True):
        query = st.text_area(
            label="Describe your ploblem",
            help="We expect you to describe the problem as detailed as possible. Our AI will make its best to extract your prior probem, possible options and preferences for further decision making."

        )
        

render_decisionpage()

