# FILESTATUS: WIP, needs testing. Last updated v0.1.2-pre3
# IMPORTS ---------------------------------------------------------------------------------
from pathlib import Path
import streamlit as st

# FUNCTIONS ---------------------------------------------------------------------------------

# get the llama.cpp dir, cached
@st.cache_data
def llama_cpp_dir():
    return Path("llama.cpp")

# get the models dir, cached
@st.cache_data
def models_dir():
    return Path("llama.cpp/models")