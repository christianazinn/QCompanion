# Last updated v0.1.2
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
    return Path("llama.cpp/models")

# get the data dir, cached
@st.cache_data
def data_dir():
    return Path("llama.cpp/data")

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
def list_data_files():
    data_files = []
    if os.path.exists(data_dir()):
        for file in os.listdir(data_dir()):
            if file.lower().endswith('.dat') or file.lower().endswith('.txt'):
                data_files.append(file)
    return data_files

# get the files from the Hugging Face repo - kept basically the same implementation as in the original
def get_files_from_repo(url, repo_name):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            files_info = response.json()
            file_info_dict = {}
            file_links_dict = {}

            base_url = f"https://huggingface.co/{repo_name}/resolve/main/"
            for file in files_info:
                name = file.get('path', 'Unknown')
                size = file.get('size', 0)
                human_readable_size = f"{size / 1024 / 1024:.2f} MB"
                file_info_dict[name] = human_readable_size
                file_links_dict[name] = base_url + name

            return file_info_dict, file_links_dict
        else:
            return {}, {}
    except Exception as e:
        return {}, {}