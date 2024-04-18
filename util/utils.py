# Last updated v0.1.3-pre1
# IMPORTS ---------------------------------------------------------------------------------
import requests
from util.paths import models_dir

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
    
# Return a high precision outfile path given model folder and conversion option for Full_Pipeline.py
def get_high_precision_outfile(model_folder, option):
    return str(models_dir() / model_folder / "High-Precision-Quantization" / f"{model_folder}-{option.lower()}.GGUF")