# Last updated 0.2.0-pre1
import sys
from huggingface_hub import snapshot_download
from util.paths import models_dir

# Simple download script. full_model_name comes in the form of "model_creator/model_name"
full_model_name = sys.argv[1]
model_creator, model_name = full_model_name.split("/")
download_path = models_dir() / model_name
download_path.mkdir(parents=True, exist_ok=True)
snapshot_download(repo_id=f"{model_creator}/{model_name}", local_dir=str(download_path))