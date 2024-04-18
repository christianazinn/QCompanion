# Last updated v0.1.3-pre1
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *
from util.paths import *

# FUNCTIONS ---------------------------------------------------------------------------------

# Trigger the conversion commands
def trigger_command(model_folder, options, vocab, ctx, pad, skip):

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
            queue_command(model_folder, option.lower(), input_dir, target_dir, vocab, ctx, pad, skip)

    return "Commands queued. They will run sequentially."


# Schedule the conversion command
def queue_command(model_folder, out_type, input_dir, target_dir, vocab, ctx, pad, skip):
    output_file = f"{model_folder}-{out_type}.GGUF"
    
    # Correct path for convert.py
    convert_script_path = llama_cpp_dir() / "convert.py" # Assuming convert.py is in llama.cpp
    
    command = [
        "python3", str(convert_script_path),
        str(input_dir),
        "--outfile", str(target_dir / output_file),
        "--outtype", out_type
    ]

    if vocab:
        command.extend(["--vocabtype", vocab])

    if ctx:
        command.extend(["--ctx", str(ctx)])

    if pad:
        command.append("--pad-vocab")

    if skip:
        command.append("--skip-unknown")

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

with st.expander("Conversion Options"):
    optcols = st.columns(4)
    
    with optcols[0]:
        use_vocab = st.checkbox("Change vocab type, --vocabtype")
        vocab = st.selectbox("Vocab type", ["spm", "bpe", "hfft"], index=0, disabled=not use_vocab)

    with optcols[1]:
        use_c = st.checkbox("Change context length, --ctx")
        c = st.number_input("Size of the prompt context, -c", value=2048, disabled=not use_c)

    with optcols[2]:
        use_pad = st.checkbox("Pad vocab, --pad-vocab")

    with optcols[3]:
        use_skip = st.checkbox("Skip unknown, --skip-unknown")

if st.button("Queue Commands"):
    if not any(options.values()):
        st.error("Please select at least one quantization type before running commands.")
    else:
        status = trigger_command(model_folder, options, vocab if use_vocab else None, c if use_c else None, use_pad, use_skip)
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