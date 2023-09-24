import streamlit as st

def start_app():
    if 'menu_option' not in st.session_state:
        st.session_state['menu_option'] = 0

    if 'job_title' not in st.session_state:
        st.session_state['job_title'] = ""

    if 'job_description' not in st.session_state:
        st.session_state['job_description'] = ""

    if 'title_placeholder' not in st.session_state:
        st.session_state['title_placeholder'] = ""

    if 'desc_placeholder' not in st.session_state:
        st.session_state['desc_placeholder'] = ""

    if 'submitted' not in st.session_state:
        st.session_state['submitted'] = False


def next_page():
    st.session_state['menu_option'] = min((st.session_state['menu_option'] + 1),3)
    selected = steps[st.session_state['menu_option']]

def prev_page():
    st.session_state['menu_option'] = max((st.session_state['menu_option'] - 1),0)
    selected = steps[st.session_state['menu_option']]

def submit():
    st.session_state['submitted'] = True
    st.balloons()
    time.sleep(2)
    st.rerun()

def reset():
    st.session_state['submitted'] = False
    st.session_state['menu_option'] = 0
    selected = steps[0]
