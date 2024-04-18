# Last updated 0.1.2
import sys
from huggingface_hub import HfApi
from requests.exceptions import HTTPError

# Simple upload script. full_model_name comes in the form of "model_creator/model_name"
token = sys.argv[1]
api = HfApi()
username = api.whoami(token=token)['name']
repo_id = f"{username}/{sys.argv[2]}"

# Check if the repository exists, if not create it
try:
    api.repo_info(repo_id=repo_id, token=token)
except HTTPError as e:
    if e.response.status_code == 404:
        api.create_repo(repo_id=repo_id, token=token, repo_type="model")
    else:
        raise

# Upload selected files
for file_name in sys.argv[3:]:
    api.upload_file(path_or_fileobj=file_name, path_in_repo=file_name, repo_id=repo_id, token=token)