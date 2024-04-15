[//]: # FILESTATUS: Needs to be pretty much entirely rewritten. Last updated v0.1.2-pre2

<h1 align="center">QCompanion</h1>

## About QCompanion

QCompanion is a fork of [Luxadevi/Ollama-Companion](https://github.com/Luxadevi/Ollama-Companion) modified to remove the Ollama components and support a more versatile quantization and finetuning workload. It's built using Streamlit to provide a web interface to a robust scheduling system that queues jobs in [llama.cpp](https://github.com/ggerganov/llama.cpp) and [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) for model quantization and finetuning, respectively, with Lilac integration coming soon. Fork it yourself or run it vanilla - your choice.

### About the scheduler

QCompanion is designed around its scheduling system, where you can schedule jobs and leave them to run later. All jobs use the same queue, from conversion to quantization to finetuning (except maybe downloading, that's a WIP), so you can leave your PC on overnight or while you're away and not worry about parallel crashes or anything. You can also edit the queue directly (e.g. to add custom commands not supported by the GUI app) by editing `util/queue.txt`.

## How to Run

### All-in-one installer ###

Clone the repository:
```
git clone https://github.com/christianazinn/QCompanion.git
sudo chmod +x install.sh
./install.sh
```

### Starting QCompanion ###
To start QCompanion locally, run
```
streamlit run Homepage.py
```
or
```
./start.sh -local
```
to run QCompanion on localhost:8501. To serve QCompanion publicly over a Cloudflare tunnel, run
```
./start.sh
```
without the -local flag.

**Note**: Windows support is currently unavailable. This project is a work in progress and both llama.cpp and LLaMA-Factory are compatible with Windows, but focus will be on adding more functionality before porting to Windows. In the meantime, you can run QCompanion on your Windows machine via the [Windows Subsystem for Linux.](https://learn.microsoft.com/en-us/windows/wsl/install)

## Add Your Own Modules
You can develop your own [Streamlit](https://streamlit.io/) components and integrate them into Ollama-Companion in the `pages` subdirectory. Add them to the page list in `Homepage.py` to be able to view them from the app itself. Be aware of the existence of the `utils` subdirectory and make good use of the stuff that's already built.

## How to Download Model Files from HuggingFace

To download model files from HuggingFace, follow these steps:

1. **Visit the Model Page**: Go to the Hugging Face model page you wish to download. For example: [MistralAI/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

2. **Copy Model Path**: On the model page, locate the icon next to the username of the model's author (usually a clipboard or copy symbol). Click to copy the model path, e.g., `mistralai/Mistral-7B-Instruct-v0.2`.

3. **Paste in the Input Field**: Paste the copied model path directly into the designated input field in your application.

4. **Get File List**: Click the "Get file list" button to retrieve a list of available files in this repository.

5. **Review File List**: Ensure the list contains the correct model files you wish to download. These will usually be `safetensors` and related files.

6. **Download Model**: Click the "Download Model" button to queue a download job for the selected files.

7. **File Storage**: The model files will be saved in the `llama.cpp/models` directory on your device.

## How to Convert Models

From a `safetensors` model in HuggingFace format, you'll need to convert and quantize it to `gguf` format for use in llama.cpp and related applications. To do this, follow these steps:

### Step One: Model Conversion with High Precision

1. **Select a Model Folder**: Choose a folder within `llama.cpp/models` that contains the model you wish to convert.

2. **Set Conversion Options**: Select your desired conversion options from the provided checkboxes: FP32, FP16, or Q8_0, in decreasing order of quality and size.

3. **Execute Conversion**: Click the "Run Commands" button to queue a conversion job.

4. **Output Location**: Converted models will be saved in the `High-Precision-Quantization` subfolder within the selected model folder.

### Step Two: Model Quantization - Q, K, and I-quants

1. **Select GGUF File**: Choose the GGUF file you wish to quantize from the dropdown list.

2. **Quantization Options**: Check the boxes next to the quantization options you want to apply. Q, K, and I-quants are supported.

3. **Run Quantization**: Click the "Run Selected Commands" button to queue the quantization jobs.

4. **Save Location**: The quantized models will be saved in the `/modelname/Medium-Precision-Quantization` folder.

## How to Upload Models

Use this section to securely upload your converted models to Hugging Face.

1. **Select a Model**: Choose a model from the dropdown list. These models are located in the `llama.cpp/models` directory.

2. **Enter Repository Name**: Specify a name for the new Hugging Face repository where your model will be uploaded.

3. **Choose Files for Upload**: Select the files you wish to upload from the subfolders of the chosen model.

4. **Add README Content**: Optionally, write content for the README.md file of your new repository.

#### Token Usage
- For enhanced security, use an encrypted token. Encrypt your Hugging Face token on the Token Encrypt page and enter it in the "Enter Encrypted Token" field.
- Alternatively, enter an unencrypted Hugging Face token directly.

5. **Upload Files**: Click the "Upload Selected Files" button to initiate the upload to Hugging Face.

After completing these steps, your uploaded models will be accessible at `https://huggingface.co/your-username/your-repo-name`.

## Upcoming Functionality

Coming soon, we have:

- Importance matrix (imatrix) support for quantization

- Options to set custom output directory and more command-line arguments (e.g. `-c`, `-b`)

- LLaMA-Factory integration for finetuning

- Lilac integration for dataset management

- GPU offload for select tasks

- Ability to queue jobs for files that don't yet exist

**Check the docs for more information!**

### License

Licensed under the Apache License.
