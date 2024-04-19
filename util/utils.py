# Last updated v0.1.3
# IMPORTS ---------------------------------------------------------------------------------
import requests, re
from util.paths import *

# FUNCTIONS ---------------------------------------------------------------------------------
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
    
# Return a high precision outfolder path and make it given model folder for Full_Pipeline.py
# model_folder is just the NAME of the folder, not its path
def get_high_precision_outdir(model_folder):
    outdir = models_dir() / model_folder / "High-Precision-Quantization"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir

# Return a medium precision outfolder path and make it given model folder for Full_Pipeline.py
# model_folder is just the NAME of the folder, not its path
def get_med_precision_outdir(model_folder):
    outdir = models_dir() / model_folder / "Medium-Precision-Quantization"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir
    
# Return a high precision outfile path given model folder and conversion option for Full_Pipeline.py
# model_folder is just the NAME of the folder, not its path
def get_high_precision_outfile(model_folder, option):
    model_folder = modify_model_file(model_folder)
    return str(get_high_precision_outdir(model_folder) / f"{model_folder}-{option.lower()}.GGUF")

# Return a medium precision outfile path given model folder and conversion option for Full_Pipeline.py
# model_folder is just the NAME of the folder, not its path
def get_med_precision_outfile(model_folder, option):
    model_file = modify_model_file(model_folder.lower())
    return str(get_med_precision_outdir(model_folder) / f"{model_file}-{option.upper()}.GGUF")

# Return an imatrix filepath given the original GGUF and the data to train it on for Full_Pipeline.py
def get_imatrix_filepath(selected_gguf_file, selected_training_data):
    gguf_path = Path(selected_gguf_file)
    model_name_only, model_file = gguf_path.parts[-3], gguf_path.name

    imatrix_dir = models_dir() / model_name_only / 'imatrix'
    imatrix_dir.mkdir(parents=True, exist_ok=True)

    modified_data = re.search(r'^.*(?=\.)', selected_training_data)[0]
    modified_model_file = f"{modify_model_file(model_file.lower())}-imatrix-{modified_data}.dat"

    return imatrix_dir / modified_model_file

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
def modify_model_file(model_file):
    return model_file.lower().replace('-f16.gguf', '').replace('-q8_0.gguf', '').replace('-f32.gguf', '')