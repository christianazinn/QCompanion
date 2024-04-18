# Last updated v0.1.2
# TODO REWRITE
docs = {
    "General information": {
        "Index": """
# Welcome to QCompanion!

Welcome to the QCompanion documentation! Use this page whenever you want to learn about certain components and pages.    
Within the pages there will also be a expander that when clicked shows a short overview of the functionality of the current page.  

* Use the sidebar on the left to navigate to the desired page.  
 

        """,

    "FAQ": """
# FAQ

* Q: How do I download models?
  - A: Use the models download page page to download and customize models, keep all parameters default and only define a name to just download default models

* What is quantization and converting of models?
  - A: This is the process of compressing models with certain qualities/sizes to a GGUF file format that llama.cpp can read
  
* Q: What models can be converted or quantized
  - A: You can convert transformers and pytorch models, some models are not supported due to the lack of information about the "TEMPLATE"
  
* Q: Why do i want to quantize or convert models on my own, thebloke does already provide GGUF files
  - A: The converting and quanting of models is build upon the same workflow as TheBloke this enables you to convert models otherwise not available in the GGUF file format for example whenever a new model releases. This also enables you to convert niche models and customize more parts. 
  
* Q: I would like to see support for X or would like X functionality
  - A: Open a issue on Github for feature requests or whenever you have cool ideas!
""",
    },
    "Converting models": {
        "General information": """
# Converting Models

Ollama-Companion offers the capability to download and convert models from HuggingFace with just a few clicks.  
This uses the same general workflow as "TheBloke" converted models.

### Steps for Model Conversion

To convert models, follow these steps:

1. **Download the Model**: Use the included downloader to obtain the model from HuggingFace.
2. **Convert to GGUF Format**: Utilize the High Precision Quantization page to convert the model into GGUF file format.
3. **Further Quantization**: Apply Medium Precision Quantization on the model through the designated page.
4. **Upload Back to HuggingFace**: After quantization, upload the models back to HuggingFace.

##### Pushing Models to Ollama Model Library

- Additionally, it is possible to push models to the open Ollama model library. This feature aims to create an extensive community-based model library.
- Note: This functionality is currently a Work In Progress. More updates and features are expected in the near future.

---
### What does it mean to quantize models?

Quantizing transformers or PyTorch large language models for use with the GGUF file format involves compressing the model to make it more efficient for deployment and execution.   

This process reduces the size of the model by converting its parameters from higher-precision formats (like 32-bit floating points) to lower-precision formats (like 8-bit integers), thereby reducing memory usage and improving computational speed. 

The GGUF file format, specifically designed for quantized models, ensures that these smaller, more efficient models are stored in an optimized manner, making them more suitable for deployment in resource-constrained environments or for applications requiring high-speed processing.
        
##### Understanding File Formats: F32, F16, Q8_0 Quantization

**F32 (32-bit Floating Point)**:
- **Precision**: High, with 32 bits per number (1 for sign, 8 for exponent, 23 for fraction).
- **Usecase**: Used for the base of a quantazing of models
- **Performance**: Requires more memory, slower processing.

**F16 (16-bit Floating Point)**:
- **Precision**: Medium, using 16 bits (1 for sign, 5 for exponent, 10 for fraction).
- **Performance**: Balances precision and performance, faster and more memory-efficient than F32.

**Q8_0 (8-bit Fixed Point)**:
- **Precision**: Low, all 8 bits for integer part, no fractional part.
- **Performance**: Highly efficient in memory and speed, but significantly lower precision.

""",
        "Download models": """
# How to Download Model Files from Hugging Face

- First, visit the Hugging Face model page that you want to download. For example, if you want to download the model at this link: [https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

- On the model page, locate the icon next to the username of the model's author. This icon typically looks like a clipboard or a copy symbol. Click on this icon to copy the Username/RepositoryName, which in this example is `mistralai/Mistral-7B-Instruct-v0.2`.

- Paste the copied Username/RepositoryName `mistralai/Mistral-7B-Instruct-v0.2` directly into the input field.

- Click the "Get file list" button or option to retrieve the list of files available in this repository.

- Review the list of files to ensure you have the correct model files that you want to download.

- Finally, click the "Download Model" button or option to initiate the download process for the selected model files.

- The model files will be saved in the `llama.cpp/models` directory on your device.

- Now you have successfully downloaded the model files from Hugging Face, and they are stored in the `llama.cpp/models` directory for your use.

        """,
    "Manually converting models": """# Convert models to GGUF.
Ollama-Companion provides the conversion of Transformer and PyTorch models to the GGUF (Generic GPU Utility Format) file format. The first step in this process involves converting a model into a format that can be further quantized, essentially creating a base for the next step in quantization.


## Steps to convert transformers model.

1. **Model to High-Quality Base File**: Begin by converting a model to a high-quality base file, setting the stage for further quantization.

2. **Use Docker for Conversion**: 
   - Enable the docker checkmark to employ a Docker container for the conversion, pulling the Companion-converter container.
   - Ensure Docker commands can run without sudo privileges.

3. **Conversion Process**: 
   - Select a model from the dropdown in the `llama.cpp/models` directory.
   - Choose the Quality/Format for conversion, including "Q8_0", "F16", or "F32".
   - Click **"Start Conversion"** to begin the process.

4. **Storage of Converted Models**: 
   - The Companion stores converted models in the `High-Precision-Quantization` folder within the `models` directory.

#### Understanding Different Format Options

- **F32 Format**: Converting to F32 (32-bit Floating Point) is the recommended approach. This format maintains a high level of precision and information quality, essential for complex computations and detailed model analyses. F32 is ideal for models where accuracy and detailed data representation are critical, making it the preferred choice for further quantization.

- **F16 Format**: F16 (16-bit Floating Point) offers a balance between performance and precision. It provides less precision than F32 but significantly reduces the model's memory requirements and increases computational speed. F16 is suited for scenarios where speed is prioritized over extreme precision.

- **Q8_0 Format**: The Q8_0 (Quantized 8-bit) format is another option, but it is generally not recommended for typical use. This format considerably reduces the model size and increases speed but at the cost of a substantial loss in precision. The Q8_0 format can lead to degraded model performance and accuracy, making it less suitable for applications where these factors are important.
# Quantize models 
After building the base file for the quantization process, proceed to the Medium Precision Quantization page. Quantizing models is necessary for their use with Ollama/llama.cpp. For optimal results, use the Q8.0 or F16 formats.  
For testing purposes, quantizing models to Q4_0 is advised as it generally offers the best compatibility. Jobs are automatically scheduled when multiple options are selected.

1. Select the model you would like to quantize from the dropdown menu.
2. Choose the quality with which you want to quantize (options include Q4.0, Q6K_M).
3. Press the **"Start quantizing"** button to initiate the quantization process.
4. The Companion stores quantized models in the Medium-Precision-Quantization sub-directory within the models folder.
""",


    "Upload Models": """
# Upload Models to HuggingFace

Use the HF Uploader page to upload models back to HuggingFace. You can create a free account at [HuggingFace](https://huggingface.co) and store files up to 100GB for free. HuggingFace also offers unlimited repository storage for files and models. For enhanced security, use an encrypted HuggingFace token.

- **Handling of the HF API Token**: During the uploading process, the HuggingFace API token is temporarily stored in its own environment variable. Once the uploading concludes, this variable is automatically deleted for security purposes.

- **Future Feature - Persistent Storage of API Token**: In future updates, there will be an option to store the HF API token indefinitely. Streamlit offers a secure vault for storing environment variables, such as API keys. However, this feature is not yet implemented in the current version of the Ollama-Companion.

#### Encrypted token

For a extra layer of security when dealing with API keys use the Token Encrypter page, this will encrypt your token and add some extra protection.
Copy your HF API token within the textarea and encrypt your token.
If you desire a new encrypton key or there is no encryption key available click the **"Generate new key"** button.

#### Steps for Uploading Models

1. **Select a Model**: Choose a model from the dropdown list found in the `llama.cpp/models` directory.
2. **Enter Repository Name**: Provide a name for the new Hugging Face repository where your model will be uploaded.
3. **Choose Files for Upload**: Select the specific files you wish to upload from the chosen model's subfolders.
4. **Add README Content**: Optionally, compose content for the README.md file of your repository.
5. **Token Usage**:
   - For added security, use an encrypted token. Encrypt your Hugging Face token on the Token Encrypt page and paste it into the "Enter Encrypted Token" field.
   - Alternatively, input an unencrypted Hugging Face token directly.
6. **Upload Files**: Click on the "Upload Selected Files" button to initiate the upload of your files to Hugging Face.  
   establishing the connection to HuggingFace can generally take a while, do not press the button multiple times.
7. **Accessing Uploaded Models**: Once uploaded, the models can be accessed at `https://huggingface.co/your-username/your-repo-name`.

"""
    },
    "Develop custom functions": {
"Tips and tricks":
 """
# How to add custom functions

To incorporate custom functions or pages into the Ollama-Companion, create a Python file in the **"pages"** directory. This approach simplifies building and adding functions. For instance, you could develop a language chain stack or construct a terminal emulator. The possibilities are endless.

Import streamlit within the just created file like this:

```
import streamlit as st
```

Now you can start writing your custom functions within this document to learn more about how to build streamlit UI elements refrence : 

[Streamlit docs](http://docs.streamlit.com)

Tips building for building with Streamlit:

- **Use Subprocess Instead of Threading**: Opt for subprocesses over threading for improved performance and management.

- **Utilize Session State or Caching**: Employ Streamlit's `session_state` or caching mechanisms to maintain data across sessions or to minimize redundant processing.

- **Self-Contained Loops**: Ensure that loops are self-contained to prevent unnecessary complications.

- **Clearly Defined Functions and UI Elements**: Use clear and distinct names for functions and UI elements, especially important when functions are used across different pages.

- **Understanding Streamlit's Threading**: Streamlit has its own threading module and recommends using this automated threading for its elements.

- **Page Changes in Streamlit**: When switching pages in Streamlit, the entire script runs again. Therefore, utilize caching or session state to optimize resource usage.

- **Naming Conventions**: Choose unique and descriptive names when developing functions for multiple pages to avoid conflicts and ensure clarity. Good naming practices are crucial for importing modules and functions on different pages effectively.

---
"""
  },
  "Finetune local models with LLaMA-Factory": {
      # TODO
  },
  "Manage data with Lilac": {
      # TODO
  }
}
