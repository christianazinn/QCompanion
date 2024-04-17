# FILESTATUS Complete and tested. Last updated 0.1.2-pre5
import sys
from huggingface_hub import snapshot_download
from pathlib import Path

# Simple download script. full_model_name comes in the form of "model_creator/model_name"
full_model_name = sys.argv[1]
model_creator, model_name = full_model_name.split("/")
download_path = Path("llama.cpp/models") / model_name
download_path.mkdir(parents=True, exist_ok=True)
snapshot_download(repo_id=f"{model_creator}/{model_name}", local_dir=str(download_path))