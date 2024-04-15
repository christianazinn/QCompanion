# FILESTATUS: the entire thing still needs to be written + implemented. Last updated v0.1.1
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from st_pages import add_indentation

# FUNCTIONS ---------------------------------------------------------------------------------

# functionality you need:
# TODO select model to create imatrix with out of fp32, int8, and fp16 - borrow code from another file for this
# TODO select data to train on
# TODO default or changeable training parameters, incl. -c 512 -b 1024 etc
# TODO verbosity should remain at 2

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Create Importance Matrix")

# TODO make the entire damn page lmao
with st.expander("What is an Importance Matrix?"):
    st.markdown("""
    An Importance Matrix is a tool used to determine the importance of each feature in a dataset. 
    It is a matrix that shows how much each feature contributes to the prediction of the target variable.
    """)