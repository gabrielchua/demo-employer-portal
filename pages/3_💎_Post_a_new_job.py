# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

from streamlit_tags import st_tags
from streamlit_option_menu import option_menu
from annotated_text import annotated_text
from streamlit_extras.switch_page_button import switch_page

from ssg_sea.extract_skills import extract_skills
import chromadb


from data.placeholder import positive_example_title, positive_example_desc, negative_example_title, negative_example_desc
from utils.llm import suggest_title, check_completeness, suggest_improvement, get_embedding, get_jtm_sector
from utils.state_management import start_app, next_page, prev_page, submit, reset
from utils.html import clean_html, get_mcf_job

import time
import ast

import urllib3


###
st.set_page_config(
    page_title="Demo - Employer Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="auto"
)


####################################################

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

def submit():
    st.session_state['submitted'] = True
    st.balloons()
    time.sleep(2)
    st.rerun()

def reset():
    st.session_state['submitted'] = False
    st.session_state['menu_option'] = 0
    selected = steps[0]

start_app()

title_placeholder = ""
desc_placeholder = ""

####################################################
st.title("Post a New Job ⚡")

st.write("This application is in Alpha (v0.0.1, last updated 09/10/2023).")
col1, col2 = st.columns(2)
col1.info("🚨 Your prompts will not be stored by commercial vendors, but will be logged in LaunchPad to improve our services. LaunchPad currently supports data classified up to Restricted and Sensitive (Normal)")
col2.info("🤝 By using the service, you acknowledge that you recognise the possibility of AI generating inaccurate or wrong responses, and you take full responsibility over how you use the generated output.")
st.warning("⚠️ This application is by powered by a Large Language Model (LLMs) and you can use it to generate job posting suggestions. Treat this as a helpful AI assistant that can provide initial ideas for you to refine")
st.warning("⚠️ Never trust the responses at face value. If in doubt, don't use the given response. ")

if st.session_state['submitted'] == False:

    with st.expander("**FOR DEMO PURPOSES ONLY**"):
        st.write(''' For this demo, you can click the button below to autofill the form or enter a MCF URL.
        ''')

        colA, colB, _ = st.columns((2,2,10))

        if colA.button("Example 1"):
            st.session_state['title_placeholder'] = positive_example_title
            st.session_state['desc_placeholder'] = positive_example_desc
        if colB.button("Example 2"):
            st.session_state['title_placeholder'] = negative_example_title
            st.session_state['desc_placeholder'] = negative_example_desc
        
        mcf_url = colA.text_input("Enter MCF URL")

        if colA.button("Get from MCF"):
            if mcf_url != "":
                http = urllib3.PoolManager()
                mcf_data = get_mcf_job(mcf_url, http)
                mcf_title = mcf_data['title']
                mcf_desc = mcf_data['description']
                mcf_desc = clean_html(mcf_desc)
                st.session_state['title_placeholder'] = mcf_title
                st.session_state['desc_placeholder'] = mcf_desc


    col0a, col0b = st.columns(2)
        
    with col0a:
        st.markdown("### Details")

        job_title = col0a.text_input("**Job Title**",
                                        value=st.session_state['title_placeholder'])
        job_description = col0a.text_area("**Job Descriptions**",
                                            height=500,
                                            value=st.session_state['desc_placeholder'])

        st.session_state['job_title'] = job_title
        st.session_state['job_description'] = job_description

        if st.button("Post ✅"):
            submit()

    with col0b:
        if job_title != "" and job_description != "":
            st.markdown("### AI Feedback")
            st.markdown("**Job Title Clarity**")

            suggestion = suggest_title(job_title, job_description)
            if suggestion == "NIL":
                st.success("The job title seems to match the description ✅")
            else:
                st.warning(f"""⚠️ You could considering adjusting the title to better match the description given. Here are some suggestions: *{suggestion}*""")

            topic_present = ast.literal_eval(check_completeness(job_description))
            st.markdown("**Topics Mentioned 📋**")
            st.success(f'''
                            
    {"✅ Working Experience" if topic_present[0]==True else "❌ Working Experience"}

    {"✅ Education" if topic_present[1]==True else "❌ Education"}

    {"✅ Language Skills" if topic_present[2]==True else "❌ Language Skills"}

    {"✅ Managerial Skills" if topic_present[3]==True else "❌ Managerial Skills"}

    {"✅ Technical Skills" if topic_present[4]==True else "❌ Technical Skills"}

    ''')
            
            jtm_sector = get_jtm_sector(st.session_state['job_title'], st.session_state['job_description'])
            client = chromadb.PersistentClient()
            collection = client.get_collection(name=jtm_sector)

            results = collection.query(query_embeddings=get_embedding(st.session_state['job_description']), n_results = 3)
            jtm_extracts = results['documents'][0]
            suggestions = suggest_improvement(st.session_state['job_title'],
                                            st.session_state['job_description'],
                                            jtm_extracts)

            st.markdown("**Job Transformation**")
            st.info(f"{suggestions}")

####################################################

else:
    st.markdown("### Thank you for posting your job")
    back_home = st.button("Back to Home 🏠")
    if back_home:
        reset()
        switch_page("home")
    st.info("For more info on Job Redesign, please contact XXX.")