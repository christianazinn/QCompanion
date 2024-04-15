# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from st_pages import add_indentation

# FUNCTIONS ---------------------------------------------------------------------------------

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Create Importance Matrix")

# TODO make the entire  damn page lmao
with st.expander("What is an Importance Matrix?"):
    st.markdown("""
    An Importance Matrix is a tool used to determine the importance of each feature in a dataset. 
    It is a matrix that shows how much each feature contributes to the prediction of the target variable.
    """)