# FILESTATUS: completed, needs testing. Last updated v0.1.2-pre5
# IMPORTS ---------------------------------------------------------------------------------
import requests, streamlit as st
st.set_page_config(layout="wide")
from pathlib import Path
from st_pages import add_indentation
from util.scheduler import *
from util.paths import *

# FUNCTIONS ---------------------------------------------------------------------------------

# queues a download task for each file in the file_links_dict
def trigger_command(model_name):
    get_scheduler().add_job(["python3", "util/download.py", model_name])

    return "Download tasks have been queued."

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

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Model Downloader")

model_name = st.text_input("Download PyTorch models from Huggingface", "Use the HuggingfaceUsername/Modelname")
if st.button("Get File List"):
    _, file_links = get_files_from_repo(f"https://huggingface.co/api/models/{model_name}/tree/main", model_name)
    if file_links:
        st.session_state['file_links_dict'] = file_links
        files_info = "\n".join(f"{name}, Size: {size}" for name, size in file_links.items())
        st.text_area("Files Information", files_info, height=300)
    else:
        st.error("Unable to retrieve file links.")
        if 'file_links_dict' in st.session_state:
            del st.session_state['file_links_dict']

if st.button("Download Files"):
    if 'file_links_dict' in st.session_state and st.session_state['file_links_dict']:
        queue_message = trigger_command(model_name)
        st.text(queue_message)
    else:
        st.error("No files to download. Please get the file list first.")

with st.expander("How to Download Model Files from Hugging Face", expanded=False):
    st.markdown("""
    1. **Visit the Model Page**: Go to the Hugging Face model page you wish to download. For example: [MistralAI/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

    2. **Copy Model Path**: On the model page, locate the icon next to the username of the model's author (usually a clipboard or copy symbol). Click to copy the model path, e.g., `mistralai/Mistral-7B-Instruct-v0.2`.

    3. **Paste in the Input Field**: Paste the copied model path directly into the designated input field in your application.

    4. **Get File List**: Click the "Get file list" button to retrieve a list of available files in this repository.

    5. **Review File List**: Ensure the list contains the correct model files you wish to download. These will usually be `safetensors` and related files.

    6. **Download Model**: Click the "Download Model" button to queue a download job for the selected files.

    7. **File Storage**: The model files will be saved in the `llama.cpp/models` directory on your device.
    """)
