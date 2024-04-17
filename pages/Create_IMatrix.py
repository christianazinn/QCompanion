# FILESTATUS: the entire thing still needs to be written + implemented. Last updated v0.1.2-pre6
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st, re
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.paths import *
from util.scheduler import *

# FUNCTIONS ---------------------------------------------------------------------------------

# functionality you need:
# TODO default or changeable training parameters, incl. -c 512 -b 1024 etc

# ./llama.cpp/imatrix -m {fp16} -f {IMATRIX} -o {imat_dat} --verbosity 2 -ngl {ngl} -c {c} -b {b} -t {t} 
# custom parameters we want: -c -b -ngl -t defaults 512 1024 NONE NONE

def trigger_command(selected_gguf_file, selected_training_data, c, b, ngl, t):
    gguf_path = Path(selected_gguf_file)
    model_name_only, model_file = gguf_path.parts[-3], gguf_path.name

    imatrix_dir = models_dir() / model_name_only / 'imatrix'
    imatrix_dir.mkdir(parents=True, exist_ok=True)

    modified_data = re.search(r'^.*(?=\.)', selected_training_data)[0]
    modified_model_file = f"{model_file.lower().replace('f16.gguf', '').replace('q8_0.gguf', '').replace('f32.gguf', '')}imatrix-{modified_data}.dat"

    output_path = imatrix_dir / modified_model_file
    data_path = data_dir() / selected_training_data
    model_path = models_dir() / model_name_only / 'High-Precision-Quantization' / model_file

    command = ["llama.cpp/imatrix", "-m", str(model_path), "-f", str(data_path), "-o", str(output_path), "--verbosity", "2",
               "-c", str(c), "-b", str(b)]
    if ngl:
        command.extend(["-ngl", str(ngl)])
    if t:
        command.extend(["-t", str(t)])
    
    get_scheduler().add_job(command)

    return "Importance Matrix creation tasks have been queued."

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Create Importance Matrix")

gguf_files = list_gguf_files()

selected_gguf_file = st.selectbox("Select a GGUF File", gguf_files)

data_files = list_data_files()

selected_training_data = st.selectbox("Select training data", data_files)

with st.expander("Optional parameters"):
    optcols = st.columns(4)

    with optcols[0]:
        use_c = st.checkbox("Change context length")
        c = st.number_input("Size of the prompt context, -c", value=512, disabled=not use_c)

    with optcols[1]:
        use_b = st.checkbox("Change processing batch size")
        b = st.number_input("Logical maximum batch size, -b", value=2048, disabled=not use_b)

    with optcols[2]:
        # only activate the ngl field if this box is checked
        use_ngl = st.checkbox("Use GPU offloading")
        ngl = st.number_input("Number of GPU offloaded layers, -ngl", value=0, disabled=not use_ngl)

    with optcols[3]:
        use_t = st.checkbox("Change thread count")
        t = st.number_input("Number of threads to use, -t", value=4, disabled=not use_t)

if st.button("Queue Importance Matrix Creation"):
    if not selected_gguf_file:
        st.error("Please select a GGUF file.")
    elif not selected_training_data:
        st.error("Please select training data.")
    else:
        status = trigger_command(selected_gguf_file, selected_training_data, c, b, ngl if use_ngl else None, t if use_t else None)
        st.text(status)

# TODO make the entire damn page lmao
with st.expander("What is an Importance Matrix?"):
    st.markdown("""
    An Importance Matrix is a tool used to determine the importance of each feature in a dataset. 
    It is a matrix that shows how much each feature contributes to the prediction of the target variable.
                
    Place data files in .dat or .txt format in the `llama.cpp/data` directory to use them for training.
    """)