# Last updated v0.1.2
# IMPORTS ---------------------------------------------------------------------------------
import os, streamlit as st
st.set_page_config(layout="wide")
from pathlib import Path
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *
from util.paths import *

# FUNCTIONS ---------------------------------------------------------------------------------

def trigger_command(modelpath, options, imatrix, nthreads):

    if not any(options.values()):
        return "Error: Please select at least one quantization option."
    
    if not list_gguf_files():
        return "Error: No GGUF files found."

    debug_output = ""
    modelpath_path = Path(modelpath)
    model_name_only, model_file = modelpath_path.parts[-3], modelpath_path.name
    base_dir = models_dir() / model_name_only
    imatrix_dir = base_dir / 'imatrix'
    medium_precision_dir = base_dir / 'Medium-Precision-Quantization'
    medium_precision_dir.mkdir(parents=True, exist_ok=True)
               
    for option, selected in options.items():
        if selected:
            source_path = base_dir / 'High-Precision-Quantization' / model_file
            modified_model_file = model_file.lower().replace('f16.gguf', '').replace('q8_0.gguf', '').replace('f32.gguf', '')
            output_path = medium_precision_dir / f"{modified_model_file}{option.upper()}.GGUF"

            debug_command_str = queue_command(source_path, output_path, option, imatrix_dir / imatrix, nthreads)
            debug_output += f"Scheduled: {debug_command_str}\n"

    return debug_output if debug_output else "No options selected."

def queue_command(source_path, output_path, option, imatrix, nthreads):
    command = [str(llama_cpp_dir() / 'quantize'), "--allow-requantize", str(source_path), str(output_path), option]

    if imatrix:
        command.insert("--imatrix", 1)
        command.insert(str(imatrix), 2)

    if nthreads:
        command.extend([str(nthreads)])

    get_scheduler().add_job(command)
    return " ".join(command)

# UI CODE ---------------------------------------------------------------------------------
# TODO can you do gpu offloading?
    
add_indentation()

st.title("Medium Precision Quantization")

gguf_files = list_gguf_files()

selected_gguf_file = st.selectbox("Select a GGUF File", gguf_files)
icol, kcol, lcol = st.columns(3)
with icol:
    st.markdown("### I-Quants")
    ioptions = {option: st.checkbox(label=option) for option in config['quantization_I']}

with kcol:
    st.markdown("### K-Quants")
    koptions = {option: st.checkbox(label=option) for option in config['quantization_K']}
    
with lcol:
    st.markdown("### Legacy Quants")
    legacy_options = {option: st.checkbox(label=option) for option in config['quantization_legacy']}

with st.expander("Optional parameters"):
    optcols = st.columns(2)

    with optcols[0]:
        use_imatrix = st.checkbox("Use importance matrix, --imatrix")
        data_files = list_imatrix_files()
        selected_training_data = st.selectbox("Select training data", data_files, disabled=not use_imatrix)

    with optcols[1]:
        use_nthreads = st.checkbox("Change thread count")
        t = st.number_input("Number of threads to use, -nthreads", value=4, disabled=not use_nthreads)

run_commands = st.button("Queue Commands")

if run_commands:
    # Check if no quantization type options are selected
    if not (any(ioptions.values()) or any(koptions.values()) or any(legacy_options.values())):
        st.error("Please select at least one quantization type before running commands.")
    # Proceed only if at least one quantization type is selected or if Docker is selected with a type
    elif any(ioptions.values()) or any(koptions.values()) or any(legacy_options.values()):
        status = trigger_command(selected_gguf_file, ioptions | koptions | legacy_options, selected_training_data if use_imatrix else None, t if use_nthreads else None)
        st.text_area("Debug Output", status, height=300)
    else:
        # This should not happen, but we include it for robustness
        st.error("Unexpected condition: No options selected.")

with st.expander("Step Two: Model Quantization - Q, K, and I-quants", expanded=False):
    st.markdown("""
    After having converted your model to a high-precision format, you may want to quantize it further to compress it and reduce its size. This page runs the `llama.cpp/quantize` script in the backend and supports any quantizations supported by your build of llama.cpp.

    1. **Select GGUF File**: Choose the GGUF file you wish to quantize from the dropdown list.

    2. **Quantization Options**: Check the boxes next to the quantization options you want to apply. Q, K, and I-quants are supported.

    3. **Run Quantization**: Click the "Run Selected Commands" button to queue the quantization jobs.

    4. **Save Location**: The quantized models will be saved in the `/modelname/Medium-Precision-Quantization` folder.
    """)

