import streamlit as st

st.set_page_config(
    page_title="Demo - Employer Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("Employer Portal Demo")

st.write("""

In this demo, we demonstrate how we can integrate job description and job design (both JDs) suggestions in the employer's user journey.
         
Leveraging LLMs, we:
- provide suggestions on the job title, where necessary
- identify if there are missing topics in the job description
- provide job design suggestion by comparing the description against the Job Transformation Maps

""")