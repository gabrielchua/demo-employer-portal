import streamlit as st
from streamlit_option_menu import option_menu

###
st.set_page_config(
    page_title="Demo - Employer Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="auto"
)

###
st.title("View Job Posting 🔍")

selected_job = st.selectbox("**Select Job**", ["<choose one>", "A", "B", "C"])

if selected_job != "<choose one>":
    st.info("*insert posted JD and AI-powered feedback*")