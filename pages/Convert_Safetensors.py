# IMPORTS ---------------------------------------------------------------------------------
import subprocess, threading, queue, streamlit as st
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *

# FUNCTIONS ---------------------------------------------------------------------------------

"""
# Initialize queue
command_queue = queue.Queue()

def process_queue():
    if not command_queue.empty():
        model_folder, out_type = command_queue.get()
        result = run_command(model_folder, out_type)
        print(result)
        command_queue.task_done()

# Set up APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(process_queue, 'interval', seconds=10)  # Adjust the interval as needed
scheduler.start()

# Initialize queue and start a background thread for processing commands
"""

# TODO fix this up and add a different command for each outtype
def run_command(model_folder, q):
    for option in q:
        if q[option]:
            out_type = option.lower()
    base_dir = Path("llama.cpp/models")
    input_dir = base_dir / model_folder
    target_dir = input_dir / "High-Precision-Quantization"
    output_file = f"{model_folder}-{out_type}.GGUF"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Correct path for convert.py
    convert_script_path = base_dir.parent / "convert.py"  # Assuming convert.py i
    
    command = [
        "python3", str(convert_script_path),
        str(input_dir),
        "--outfile", str(target_dir / output_file),
        "--outtype", out_type.lower()
    ]
    return command
    return f"python3 {str(convert_script_path)} {str(input_dir)} --outfile {str(target_dir / output_file)} --outtype {out_type.lower()}"

    """
    try:
        subprocess.run(command, check=True)
        return "Command completed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error in command execution: {e}"


def trigger_command(model_folder, options):
    if not any(options.values()):
        return "Error: No quantization type selected."
    for option in options:
        if options[option]:
            command_queue.put((model_folder, option.lower()))
    return "Commands queued. They will run sequentially."
"""


# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("High Precision Quantization")

models_dir = Path("llama.cpp/models")
model_folders = [f.name for f in models_dir.iterdir() if f.is_dir()] if models_dir.exists() else ["Directory not found"]

model_folder = st.selectbox("Select a Model Folder", model_folders)
options = {option: st.checkbox(label=option) for option in config['conversion_quants']}

if st.button("Run Commands"):
    if not any(options.values()):
        st.error("Please select at least one quantization type before running commands.")
    else:
        # status = trigger_command(model_folder, options)
        schedule = scheduler()
        schedule.add_job(run_command(model_folder, options))
        # st.text(status)


with st.expander("Step One: Model Conversion with High Precision", expanded=False):
    st.markdown("""
    **Step One: Model Conversion with High Precision**


    **Conversion Process:**

    1. **Select a Model Folder:** Choose a folder containing the model you wish to convert, found within `llama.cpp/models`.
    2. **Set Conversion Options:** Select the desired conversion options from the provided checkboxes (e.g., Q, Kquants).
    3. **Docker Container Option:** Opt to use a Docker container for added flexibility and compatibility.
    4. **Execute Conversion:** Click the "Run Commands" button to start the conversion process.
    5. **Output Location:** Converted models will be saved in the `High-Precision-Quantization` subfolder within the chosen model folder.

    Utilize this process to efficiently convert models while maintaining high precision and compatibility with `llama.cpp`.
    """)

# Start the thread to process commands
# threading.Thread(target=process_queue, daemon=True).start()
