import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from utils.html import color_table_headers

###
st.set_page_config(
    page_title="Demo - Employer Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="auto"
)

with st.expander("**Disclaimer**"):
    st.write('''
        This is a demo.
    ''')



st.title("Employer Portal 💼")

df = pd.read_csv("data/listings.csv")

df_html = df.style.hide(axis="index").to_html()
df_html = color_table_headers(df_html, bg_color="#ADD8E6")

st.markdown(df_html, unsafe_allow_html=True)