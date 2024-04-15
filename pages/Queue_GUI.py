import streamlit as st
from st_pages import add_indentation
from util.scheduler import *

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

if st.button('Run'):
    scheduler().toggle()