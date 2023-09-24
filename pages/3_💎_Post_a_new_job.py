__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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

steps = ["Step 1: Details", "Step 2: Skills", "Step 3: Additional Info", "Step 4: Review"]
num_steps = len(steps)
selected = steps[0]

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

start_app()

title_placeholder = ""
desc_placeholder = ""

####################################################
st.title("Post a New Job ⚡")

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



    selected = option_menu(None,
                        steps,
                        icons=['pen', 'task', 'search', 'check-circle'],
                        orientation="horizontal",
                        manual_select=st.session_state['menu_option'])

    for step_num in range(num_steps):
        if (selected == steps[step_num]):
            st.session_state['menu_option'] = step_num

####################################################
    if (selected == steps[0]) or (st.session_state['menu_option'] == 0):
        col0a, col0b = st.columns((3,1))
        
        with col0a:
            st.markdown("### Details")

            job_title = col0a.text_input("**Job Title**",
                                         value=st.session_state['title_placeholder'])
            job_description = col0a.text_area("**Job Descriptions**",
                                              height=500,
                                              value=st.session_state['desc_placeholder'])

            st.session_state['job_title'] = job_title
            st.session_state['job_description'] = job_description

            # _, col0aii = st.columns((9.6, 1.4))
            # with col0aii:
            #     selected_next = st.button("Next ⏩")

            #     if selected_next:
            #         if job_title == "" and job_description == "":
            #             col0a.error("Please enter the job title and description.")
            #         else:
            #             st.session_state['job_title'] = job_title
            #             st.session_state['job_description'] = job_description
            #             next_page()

        with col0b:
            if job_title != "" and job_description != "":
                st.markdown("### Feedback")
                st.markdown("**Feedback on Job Title Clarity**")

                suggestion = suggest_title(job_title, job_description)
                if suggestion == "NIL":
                    st.success("The job title seems to match the description ✅")
                else:
                    st.warning(f"""⚠️ You could considering adjusting the title to better match the description given. Here are some suggestions: *{suggestion}*""")

                topic_present = ast.literal_eval(check_completeness(job_description))
                st.markdown("**Topics Mentioned 📋**")
                st.success(f'''
                           
{"✅ Benefits" if topic_present[0]==True else "❌ Benefits"}

{"✅ Working Experience" if topic_present[1]==True else "❌ Working Experience"}

{"✅ Education" if topic_present[2]==True else "❌ Education"}

{"✅ Language Skills" if topic_present[3]==True else "❌ Language Skills"}

{"✅ Managerial Skills" if topic_present[4]==True else "❌ Managerial Skills"}

{"✅ Technical Skills" if topic_present[5]==True else "❌ Technical Skills"}

{"✅ Remote Work" if topic_present[6]==True else "❌ Remote Work"}

{"✅ Location" if topic_present[7]==True else "❌ Location"}
                           
                           ''')

####################################################
    elif (selected == steps[1]) or (st.session_state['menu_option'] == 1):

        st.markdown("## As per today, skills are extracted and auto-populated. This demo uses SSG's Skills Extraction Algo.")

        try:
            skill_list = extract_skills(st.session_state['job_description'])
            skill_list = skill_list['extractions']
            extraction_keys = skill_list.keys()
            extraction_keys = list(extraction_keys)
            extracted_skills = [skill_list[extraction_keys[i]]['skill_title'] for i in range(len(extraction_keys))]
        except:
            extracted_skills = []

        skills = st_tags(
            label='**Skills Required:**',
            text='Press enter to add more',
            value=extracted_skills)

        # col1a, _, col1c = st.columns((1, 9, 1))

        # with col1a:
        #     if st.button("⏪ Back"):
        #         prev_page()
        
        # with col1c:
        #     if st.button("Next ⏩"):
        #         next_page()

####################################################
    elif (selected == steps[2]) or (st.session_state['menu_option'] == 2):

        st.markdown("## Insert other fields (e.g. salary, number of vacancies) as per today")

        # col2a, _, col2c = st.columns((1, 9, 1))

        # with col2a:
        #     if st.button("⏪ Back"):
        #         prev_page()

        # with col2c:
        #     if st.button("Next  ⏩"):
        #         next_page()

####################################################
    elif (selected == steps[3]) or (st.session_state['menu_option'] == 3):
        col3a, col3b = st.columns((10, 1))

        col3a.info(f'''
                
**Title:** {st.session_state['job_title']}
        
**Description:** 

{st.session_state['job_description']}

        ''')

        # with col3a:
        #     if st.button("⏪ Back"):
        #         prev_page()

        with col3b:
            if st.button("Post ✅"):
                submit()

####################################################

else:
    st.markdown("### Thank you for posting your job")
    back_home = st.button("Back to Home 🏠")
    if back_home:
        reset()
        switch_page("home")

    with st.expander("**DEMO NOTE**"):
        st.write(''' The suggestions are based off the Job Transformation Map Report''')


    colZ1, colZ2 = st.columns(2)
    colZ1.markdown("### Your Posting")
    colZ1.success(f'''
                
**Title:** {st.session_state['job_title']}
    
**Description:** 

{st.session_state['job_description']}
''')
    

    jtm_sector = get_jtm_sector(st.session_state['job_title'], st.session_state['job_description'])
    client = chromadb.PersistentClient()
    collection = client.get_collection(name=jtm_sector)


    results = collection.query(query_embeddings=get_embedding(st.session_state['job_description']), n_results = 3)
    jtm_extracts = results['documents'][0]
    suggestions = suggest_improvement(st.session_state['job_title'],
                                      st.session_state['job_description'],
                                      jtm_extracts)

    colZ2.markdown("### Suggestions based on JTM")
    colZ2.info(f"{suggestions}")