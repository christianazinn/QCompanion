# FILESTATUS: entire page needs to be written + implemented. Last updated v0.1.2-pre2
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from st_pages import add_indentation
from util.scheduler import *

# FUNCTIONS ---------------------------------------------------------------------------------

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

if st.button('Run'):
    get_scheduler().toggle()

# functionality you need:
# TODO show queue and completed jobs
# TODO show active status and allow toggle
# TODO be able to reorder and move tasks in queue - pip install streamlit-sortables
# TODO ^ write rearrange_all_jobs(self, positions) in util.scheduler.py
# TODO be able to delete tasks in queue

st.write(get_scheduler().active)