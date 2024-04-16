# FILESTATUS: pretty much done, needs testing. Last updated v0.1.2-pre3
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *
from util.paths import *

# FUNCTIONS ---------------------------------------------------------------------------------
# TODO implement gpu offload at some point and be able to change output directory

# Trigger the conversion commands
def trigger_command(model_folder, options):

    # Check if any quantization type is selected
    if not any(options.values()):
        return "Error: No quantization type selected."
    
    # setup
    base_dir = models_dir()
    input_dir = base_dir / model_folder
    target_dir = input_dir / "High-Precision-Quantization"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Queue the commands
    for option, selected in options.items():
        if selected:
            queue_command(model_folder, option.lower(), base_dir, input_dir, target_dir)

    return "Commands queued. They will run sequentially."


# Schedule the conversion command
def queue_command(model_folder, out_type, base_dir, input_dir, target_dir):
    output_file = f"{model_folder}-{out_type}.GGUF"
    
    # Correct path for convert.py
    convert_script_path = base_dir.parent / "convert.py" # Assuming convert.py is in llama.cpp
    
    command = [
        "python3", str(convert_script_path),
        str(input_dir),
        "--outfile", str(target_dir / output_file),
        "--outtype", out_type
    ]

    # add to scheduler
    get_scheduler().add_job(command)


# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("High Precision Quantization")

model_folders = [f.name for f in models_dir().iterdir() if f.is_dir()] if models_dir().exists() else ["Directory not found"]

model_folder = st.selectbox("Select a Model Folder", model_folders)

conversion_cols = st.columns(len(config['conversion_quants']))
options = {}
for i in range(0, len(config['conversion_quants'])):
    with conversion_cols[i]:
        option = config['conversion_quants'][i]
        options.update({option: st.checkbox(label=option)})

# options = {option: st.checkbox(label=option) for option in config['conversion_quants']}

if st.button("Run Commands"):
    if not any(options.values()):
        st.error("Please select at least one quantization type before running commands.")
    else:
        status = trigger_command(model_folder, options)
        st.text(status)


with st.expander("Step One: Model Conversion with High Precision", expanded=False):
    st.markdown("""
    Use this page to convert models from the `safetensors` format to the `gguf` format in high precision. It runs the `llama.cpp/convert.py` script in the backend.
                
    **Usage Instructions**
    
    1. **Select a Model Folder**: Choose a folder within `llama.cpp/models` that contains the model you wish to convert.

    2. **Set Conversion Options**: Select your desired conversion options from the provided checkboxes: FP32, FP16, or Q8_0, in decreasing order of quality and size.

    3. **Execute Conversion**: Click the "Run Commands" button to queue a conversion job.

    4. **Output Location**: Converted models will be saved in the `High-Precision-Quantization` subfolder within the selected model folder.

    Utilize this process to efficiently convert models while maintaining high precision and compatibility with `llama.cpp`.
    """)