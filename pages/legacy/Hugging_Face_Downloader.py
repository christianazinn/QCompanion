# Last updated v0.1.3
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.scheduler import *
from util.utils import get_files_from_repo

# FUNCTIONS ---------------------------------------------------------------------------------

# queues a download task for each file in the file_links_dict
def trigger_command(model_name):
    get_scheduler().add_job(["python3", "util/download.py", model_name])

    return "Download tasks have been queued."

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

if st.button("Queue File Downloads"):
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
