# Last updated v0.2.0-pre1
# IMPORTS ---------------------------------------------------------------------------------
from pathlib import Path
import streamlit as st, os

# FUNCTIONS ---------------------------------------------------------------------------------

# get the llama.cpp dir, cached
@st.cache_data
def llama_cpp_dir():
    return Path("llama.cpp")

# get the models dir, cached
@st.cache_data
def models_dir():
    return Path("user/models")

# get the imatrix data dir, cached
@st.cache_data
def imatrix_data_dir():
    return Path("user/imatrix_data")

# get the llamafactory dir, cached
@st.cache_data
def llamafactory_dir():
    return Path("LLaMA-Factory")

# get the data dir, cached
@st.cache_data
def data_dir():
    return Path("user/data")

# List valid, selectable GGUF files in the models directory
def list_gguf_files():
    return list_modelspecific_files("gguf")

# List valid, selectable imatrix files in the models directory
def list_imatrix_files():
    return list_modelspecific_files("imatrix")

# code reuse
def list_modelspecific_files(intype):
    folder_name = "High-Precision-Quantization" if intype == "gguf" else "imatrix"
    file_ending = ".gguf" if intype == "gguf" else ".dat"
    files = []
    if os.path.exists(models_dir()):
        for model_folder in os.listdir(models_dir()):
            folder = os.path.join(models_dir(), model_folder, folder_name)
            if os.path.exists(folder) and os.path.isdir(folder):
                for file in os.listdir(folder):
                    if file.lower().endswith(file_ending):
                        files.append(os.path.join(model_folder, folder_name, file))
    return files

# List valid, selectable data files in the data directory
def list_imatrix_data_files():
    data_files = []
    if os.path.exists(imatrix_data_dir()):
        for file in os.listdir(imatrix_data_dir()):
            if file.lower().endswith('.dat') or file.lower().endswith('.txt'):
                data_files.append(file)
    return data_files