import openai
import streamlit as st

openai.api_type = 'azure'
openai.api_base = st.secrets["launchpad_url"]
openai.api_version = '2023-03-15-preview'
openai.api_key = st.secrets["launchpad_key"]

sys_msg_title_improvement = """

Your only task is to rate the accuracy and precision of a job title based on a given job description.
ONLY if the job title is not accurate or precision, provide THREE alternative titles.

You will receive as input: JOB TITLE, JOB DESCRIPTION in a tuple.
If the title is clear, your output will be "NIL".
If the title is not clear, your output will be the new job title, without any elaboration or explanation.

Generic titles like "manager" or "assistant" would be considered not clear.

For example,
INPUT: (Data Scientist, Builds Machine Learning Products)
OUTPUT: NIL

INPUT: (Analyst, Does business reporting with dashboarding and uses SQL)
OUTPUT: Business Intelligence Analyst, Data Analyst, BI Analyst

"""


sys_msg_jd_completeness = """

Your only task is to check if the topics, delimited by ###, are mentioned in the given job description.

You will receive as input the JOB DESCRIPTION.
You will output a python list of 8 elements, which are either True or False. You will not include any elaboration or explanation.
If the topic below is mentioned in the job description, reply True. Else, reply False

TOPICS
###
Benefits
Working Experience
Education
Language Skills
Managerial Skills
Technical Skills
Remote Work
Location
####

For example,
INPUT: JOB DESCRIPTION: Write code
OUTPUT: [False, False, False, False, False, False, False, False]



"""

sys_msg_jd_improvement = """

You are a job re-design consultant in Singapore helping company. increase their productivity and increase talent attraction.
You will receive a job description and extracts from Singapore's Job Transformation Map reports. The reports outline how jobs will need to evolve in the future.
You shall provide actionable recommendations to improve the JD/job based on the report's extracts.
You will provide at least 3 suggestions, and always format them in this format

**Suggestion 1:** <summary>

<elaboration>

**Suggestion 2:** <summary>

<elaboration>

**Suggestion 3:** <summary>

<elaboration>



"""

sys_msg_find_jtm = """

Your task is choose ONLY one of the categories delimited by "###" below that best fits the given job description.

Your reply is to contain only the category name. Do not include commas in your reply.

EXAMPLE OUTPUT: <category_name>

###
accounting
built_environment
financial_services
food_manufacturing
food_services
hotel
human_resources
in_house_corporate_finance_and_accounting
information_and_communications
land_transport
logistics
retail
supply_chain
waste_management
wholesale_trade

"""


#########
def suggest_title(title, desc):
    prompt = f"({title}, {desc})"
    title_suggestion = query_llm(sys_msg_title_improvement, prompt)
    return title_suggestion


def check_completeness(desc):
    return query_llm(sys_msg_jd_completeness, desc)


def suggest_improvement(title, desc, jtm_extracts):

    prompt = f"""
            The job description for {title} is delimited by "###", and report extracts delimited by "$$$"

            ###
            {desc}

            $$$
            {jtm_extracts[0]}
            {jtm_extracts[1]}
            {jtm_extracts[2]}
    """

    return query_llm(sys_msg_jd_improvement, prompt)

def get_jtm_sector(title, desc):
    prompt = f"""
    
    title: {title}
    
    description: {desc}
    """
    return query_llm(sys_msg_find_jtm, prompt)


def query_llm(system_message, query):
    reply = openai.ChatCompletion.create(
                    engine="gpt-35-turbo",
                    messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": query},
                        ]
                    )
    reply = reply["choices"][0]["message"]["content"]
    return reply

def get_embedding(text, engine="text-embedding-ada-002"):
   embeddings = openai.Embedding.create(input = [text], engine=engine)['data'][0]['embedding']
   return embeddings