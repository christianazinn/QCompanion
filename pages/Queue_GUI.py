# FILESTATUS: entire page needs to be written + implemented
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from st_pages import add_indentation
from util.scheduler import *

# FUNCTIONS ---------------------------------------------------------------------------------

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

if st.button('Run'):
    get_scheduler().toggle()

st.write(get_scheduler().active)