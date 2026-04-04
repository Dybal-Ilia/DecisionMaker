import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from st_module import get_event_loop
from st_module import get_drafter_agent


@st.fragment
def render_clarifications_form(clarifications_list):
    st.markdown("### Clarifications Needed")
    st.write("The AI needs a few more details to finalize your draft:")

    with st.form(key="clarifications_form"):
        temp_responses = {}

        for i, question in enumerate(clarifications_list):
            temp_responses[question] = st.text_input(question, key=f"clarification_{i}")

        submitted = st.form_submit_button("Save Answers")

        if submitted:
            final_qa_dict = {q: a for q, a in temp_responses.items() if a.strip()}
            st.session_state.draft_clarifications = final_qa_dict

            st.success("Answers saved successfully!")


def render_draft(draft):
    st.session_state.current_draft = draft

    st.success(
        "We've prepared a draft for better observability. Make sure to fill up follow-up questions and click 'Make a Decision' if everythin is correct"
    )
    st.divider()
    st.markdown(f"### {draft.general_intent} Draft")

    st.markdown("#### Options:")

    options_text = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(
        [f"*{opt}*" for opt in draft.options]
    )
    st.markdown(options_text)

    st.write("")

    st.markdown("### Preferences:")
    for pref in draft.preferences:
        st.markdown(f"✓ {pref}")

    st.write("")

    render_clarifications_form(draft.clarifications)


def render_decisionpage():
    loop = get_event_loop()
    drafter = get_drafter_agent()
    st.header("Make a Decision")
    st.divider()
    with st.container(border=True):
        query = st.text_area(
            label="Describe your ploblem",
            help="We expect you to describe the problem as detailed as possible. Our AI will make its best to extract your prior probem, possible options and preferences for further decision making.",
        )
        if st.button("Generate Draft"):
            draft = loop.run_until_complete(drafter.generate_draft(query))
            if draft is not None:
                render_draft(draft)

            st.button("Generate a Decision")
