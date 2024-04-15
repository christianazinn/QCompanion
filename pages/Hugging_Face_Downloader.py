# FILESTATUS: needs to be migrated to the New Way of Doing Things
# IMPORTS ---------------------------------------------------------------------------------
import requests, streamlit as st
from pathlib import Path
from st_pages import add_indentation
from util.scheduler import *

# FUNCTIONS ---------------------------------------------------------------------------------

# write the download task to the queue
def queue_command(file_url, download_path, filename):
    command = [
        "aria2c", file_url,
        "--max-connection-per-server=16", "--split=8", "--min-split-size=25M", "--allow-overwrite=true",
        "-d", str(download_path), "-o", filename,
        "--continue=true"
    ]
    get_scheduler.add_job(command)

# queues a download task for each file in the file_links_dict
def trigger_command(file_links_dict, model_name):
    folder_name = model_name.split("/")[-1]
    download_path = Path("llama.cpp/models") / folder_name
    download_path.mkdir(parents=True, exist_ok=True)

    for file_name, file_url in file_links_dict.items():
        filename = Path(file_name).name
        queue_command(file_url, download_path, filename)

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
        queue_message = trigger_command(st.session_state['file_links_dict'], model_name)
        st.text(queue_message)
    else:
        st.error("No files to download. Please get the file list first.")

with st.expander("How to Download Model Files from Hugging Face", expanded=False):
    st.markdown("""
    **How to Download Model Files from Hugging Face**

    - First, visit the Hugging Face model page that you want to download. For example, if you want to download the model at this link: [https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

    - On the model page, locate the icon next to the username of the model's author. This icon typically looks like a clipboard or a copy symbol. Click on this icon to copy the Username/RepositoryName, which in this example is `mistralai/Mistral-7B-Instruct-v0.2`.

    - Paste the copied Username/RepositoryName `mistralai/Mistral-7B-Instruct-v0.2` directly into the input field.

    - Click the "Get file list" button or option to retrieve the list of files available in this repository.

    - Review the list of files to ensure you have the correct model files that you want to download.

    - Finally, click the "Download Model" button or option to initiate the download process for the selected model files.

    - The model files will be saved in the `llama.cpp/models` directory on your device.

    - Now you have successfully downloaded the model files from Hugging Face, and they are stored in the `llama.cpp/models` directory for your use.
    """)
