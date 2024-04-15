# FILESTATUS: pretty much done but needs to have docs written in util.docs_inline
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from util.docs_inline import docs
from st_pages import add_indentation

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

# Create Tabs for Main Subjects
tab_main = st.tabs(list(docs.keys()))

for i, subject in enumerate(docs.keys()):
    with tab_main[i]:
        # Create Tabs for Sub-Subjects within each Main Subject
        tab_sub = st.tabs(list(docs[subject].keys()))

        for j, sub_subject in enumerate(docs[subject].keys()):
            with tab_sub[j]:
                # Display the Documentation for each Sub-Subject
                st.markdown(docs[subject][sub_subject])# st.divider()

