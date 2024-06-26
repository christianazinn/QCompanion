# Last updated v0.1.3
# IMPORTS ---------------------------------------------------------------------------------
import os, streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.paths import *
from util.scheduler import *
from util.key import decrypt_token

# FUNCTIONS ---------------------------------------------------------------------------------

# Gathers files and uploads to HuggingFace
def trigger_command(token, repo_name, files_to_upload, high_precision_files, medium_precision_files, selected_model):
    final_upload = []

    # Rename particular filepaths
    for file_name in files_to_upload:
        if file_name in high_precision_files.get(selected_model, []):
            folder_path = models_dir() / selected_model / "High-Precision-Quantization"
        elif file_name in medium_precision_files.get(selected_model, []):
            folder_path = models_dir() / selected_model / "Medium-Precision-Quantization"
        else:
            continue

        file_path = folder_path / file_name
        final_upload.append(str(file_path))

    command = ["python3", "util/upload.py", token, repo_name, *final_upload]
    get_scheduler().add_job(command)
    return "Upload tasks have been queued."

# Cache the function to improve performance
@st.cache_data
def list_model_files(subfolder):
    model_files = {}
    models_dir_path = models_dir()
    if models_dir_path.exists() and models_dir_path.is_dir():
        for model_folder in models_dir_path.iterdir():
            specific_folder = model_folder / subfolder
            if specific_folder.exists() and specific_folder.is_dir():
                model_files[model_folder.name] = [file.name for file in specific_folder.iterdir() if file.is_file()]
    return model_files

# List files in High-Precision and Medium-Precision folders
high_precision_files = list_model_files("High-Precision-Quantization")
medium_precision_files = list_model_files("Medium-Precision-Quantization")

# After calling list_model_files, check the contents
# print("High Precision Files:", high_precision_files)
# print("Medium Precision Files:", medium_precision_files)

def get_combined_files(model):
    # Combine files from both precision types
    return high_precision_files.get(model, []) + medium_precision_files.get(model, [])

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

# Main UI
st.title("Upload Converted Models to HuggingFace")

# Select a model
all_models = list(set(high_precision_files.keys()) | set(medium_precision_files.keys()))
selected_model = st.selectbox("Select a Model", all_models, index=0)

# File selection multiselect
combined_files = get_combined_files(selected_model)
selected_files = st.multiselect("Select Files to Upload", combined_files, key="file_selector")


# Repository details and README content
repo_name = st.text_input("Repository Name", value=f"{selected_model}-gguf")

# Token input
use_unencrypted_token = st.checkbox("Unencrypted Token")
if use_unencrypted_token:
    hf_token = st.text_input("Hugging Face Token", type="password")
else:
    encrypted_token = st.text_input("Enter Encrypted Token", type="password")
    if encrypted_token:
        hf_token = decrypt_token(encrypted_token)

# Upload button
if st.button("Queue File Uploads") and hf_token:
    upload_message = trigger_command(hf_token, repo_name, selected_files, high_precision_files, medium_precision_files, selected_model)
    st.info(upload_message)

if 'HUGGINGFACE_TOKEN' in os.environ:
    del os.environ['HUGGINGFACE_TOKEN']

with st.expander("Model Upload Instructions", expanded=False):
    st.markdown("""
    **Model Upload Instructions**

    Use this section to upload your converted models to Hugging Face with enhanced security.

    **Steps for Uploading Models:**

    1. **Select a Model:** Choose a model from the dropdown list. These models are found in the `llama.cpp/models` directory.
    2. **Enter Repository Name:** Specify a name for the new Hugging Face repository where your model will be uploaded.
    3. **Choose Files for Upload:** Select the files you want to upload from the chosen model's subfolders.
    4. **Add README Content:** Optionally, write content for the README.md file of your repository.
    5. **Token Usage:**
        - For added security, use an encrypted token. Encrypt your Hugging Face token on the **Token Encrypt** page and paste it into the "Enter Encrypted Token" field.
        - Alternatively, you can directly enter an unencrypted Hugging Face token.
    6. **Upload Files:** Click the "Upload Selected Files" button to start uploading your files to Hugging Face.

    The uploaded models will be viewable at `https://huggingface.co/your-username/your-repo-name`.
    """)
