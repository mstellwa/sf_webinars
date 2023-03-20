import streamlit as st
from lib.snf_utilities import create_session

st.title("Titanic Survival Application!")
st.image(r"titanic.jpeg", caption="'RMS Titanic'",use_column_width=True)

# Connect to Snowflake
create_session()

st.write("### Analyse survival first or go direct to predict to test if you will survive!")