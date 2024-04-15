# FILESTATUS: needs to be migrated to the New Way of Doing Things. Last updated v0.1.2-pre2
# IMPORTS ---------------------------------------------------------------------------------
import os, subprocess, sys, streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from st_pages import add_indentation
from util.constants import config

# FUNCTIONS ---------------------------------------------------------------------------------
# TODO dont forget to implement imatrices somehow + gpu offloading, figure out --allow-requantize and --imatrix
# TODO be able to change output directory + add support for other options like -c

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def list_gguf_files(models_dir):
    gguf_files = []
    if os.path.exists(models_dir):
        for model_folder in os.listdir(models_dir):
            hpq_folder = os.path.join(models_dir, model_folder, 'High-Precision-Quantization')
            if os.path.exists(hpq_folder) and os.path.isdir(hpq_folder):
                for file in os.listdir(hpq_folder):
                    if file.lower().endswith('.gguf'):
                        gguf_files.append(os.path.join(model_folder, 'High-Precision-Quantization', file))
    return gguf_files

def schedule_quantize_task(command):
    try:
        subprocess.run(command, check=True)
        return f"Task completed: {' '.join(command)}"
    except subprocess.CalledProcessError as e:
        return f"Error in task execution: {e}"

def trigger_command(modelpath, options):
    if not any(options.values()):
        return "Error: Please select at least one quantization option."

    debug_output = ""
    llama_cpp_dir = Path("llama.cpp")
    if llama_cpp_dir:
        base_dir = llama_cpp_dir / 'models'
        gguf_files = list_gguf_files(base_dir)
    else:
        base_dir = 'llama.cpp/models'
        models_dir = os.path.join(base_dir)
        gguf_files = list_gguf_files(models_dir)

    if not gguf_files:
        st.warning("No GGUF files found using the new logic. Falling back to the old logic.")
        base_dir = 'llama.cpp/models'
        models_dir = os.path.join(base_dir)
        gguf_files = list_gguf_files(models_dir)

    modelpath_path = Path(modelpath)
    model_name_only, model_file = modelpath_path.parts[-3], modelpath_path.name
    medium_precision_dir = base_dir / model_name_only / 'Medium-Precision-Quantization'
    medium_precision_dir.mkdir(parents=True, exist_ok=True)
               
    for option, selected in options.items():
        if selected:
            source_path = base_dir / model_name_only / 'High-Precision-Quantization' / model_file
            modified_model_file = model_file.lower().replace('f16.gguf', '').replace('q8_0.gguf', '').replace('f32.gguf', '')
            output_path = medium_precision_dir / f"{modified_model_file}-{option.upper()}.GGUF"

            # if sys.platform == "linux":
            #    command = [str(base_dir.parent / 'quantize'), str(source_path), str(output_path), option]
            # else:
            command = [str(llama_cpp_dir / 'quantize'), str(source_path), str(output_path), option]

            print(command)

            scheduler.add_job(schedule_quantize_task, args=[command])
            debug_command_str = ' '.join(command)
            debug_output += f"Scheduled: {debug_command_str}\n"

    return debug_output if debug_output else "No options selected."

# UI CODE ---------------------------------------------------------------------------------
    
add_indentation()

st.title("Medium Precision Quantization")

models_dir = os.path.join("llama.cpp", "models")
gguf_files = list_gguf_files(models_dir)

selected_gguf_file = st.selectbox("Select a GGUF File", gguf_files)
options = {option: st.checkbox(label=option) for option in config['quantization_I'] + config['quantization_K']}

run_commands = st.button("Run Selected Commands")

if run_commands:
    # Check if no quantization type options are selected
    if not any(options.values()):
        st.error("Please select at least one quantization type before running commands.")
    # Proceed only if at least one quantization type is selected or if Docker is selected with a type
    elif any(options.values()):
        status = trigger_command(selected_gguf_file, options)
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

