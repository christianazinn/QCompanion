# Last updated v0.1.3-pre1
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *
from util.paths import *
from util.utils import *

# FUNCTIONS ---------------------------------------------------------------------------------

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Full Pipeline Queue")

# Let the user decide which steps to use:
# Download can be used on its own
# Convert must either be used with Download or with a supplied model folder but is not required
# Quantize must either be used with Convert or with a supplied high-precision model but is not required
# Upload must be used with Quantize but is not required

st.markdown("Select which steps to use.")
optcols = st.columns(5)
with optcols[0]:
    download = st.checkbox("Download", value=True)

with optcols[1]:
    convert = st.checkbox("Convert")

with optcols[2]:
    imatrix = st.checkbox("Imatrix")

with optcols[3]:
    quantize = st.checkbox("Quantize")

with optcols[4]:
    upload = st.checkbox("Upload")

# Download
# DONE
if download:
    st.write("----")
    st.markdown("### Download from HuggingFace")
    model_name = st.text_input("Download PyTorch models from Huggingface", "Use the HuggingfaceUsername/Modelname")
    if st.button("Get File List"):
        _, file_links = get_files_from_repo(f"https://huggingface.co/api/models/{model_name}/tree/main", model_name)
        if file_links:
            st.session_state['file_links_dict'] = file_links
            st.session_state['model_name'] = model_name
            files_info = "\n".join(f"{name}, Size: {size}" for name, size in file_links.items())
            st.text_area("Files Information", files_info, height=300)
        else:
            st.error("Unable to retrieve file links.")
            if 'file_links_dict' in st.session_state:
                del st.session_state['file_links_dict']
                del st.session_state['model_name']
else: # if download is not selected, remove the file_links_dict and model_name from the session state
    if 'file_links_dict' in st.session_state:
        del st.session_state['file_links_dict']
        del st.session_state['model_name']

# Convert
# TODO
if convert:
    st.write("----")
    st.markdown("### Convert Safetensors to High Precision")
    if download: # automatically determine where download.py will download it
        if 'model_name' in st.session_state:
            original_model_name = st.session_state['model_name'].split("/")[1]
            convert_model_folder = models_dir() / original_model_name
            st.markdown(f"Using to-be-created model directory `{convert_model_folder}`")
        else:
            st.error("Please choose a model to download first.")
    else:
        convert_model_folders = [f.name for f in models_dir().iterdir() if f.is_dir()] if models_dir().exists() else ["Directory not found"]
        convert_model_folder = st.selectbox("Select a model folder", convert_model_folders, key="convert_select_folder")

    # write conversion options (fp16, fp32, int8)
    conversion_cols = st.columns(len(config['conversion_quants']))
    conversion_options = {}
    for i in range(0, len(config['conversion_quants'])):
        with conversion_cols[i]:
            option = config['conversion_quants'][i]
            conversion_options.update({option: st.checkbox(label=option, key=f"convert_{option}")})

    # write cli flags (vocab, ctx, pad, skip)
    with st.expander("Options/flags for conversion"):
        conversion_optcols = st.columns(4)
        
        with conversion_optcols[0]:
            conversion_use_vocab = st.checkbox("Change vocab type, --vocabtype", key="convert_use_vocab")
            conversion_vocab = st.selectbox("Vocab type", ["spm", "bpe", "hfft"], index=0, disabled=not conversion_use_vocab, key="convert_vocab")

        with conversion_optcols[1]:
            conversion_use_c = st.checkbox("Change context length, --ctx", key="convert_use_c")
            conversion_c = st.number_input("Size of the prompt context, -c", value=2048, disabled=not conversion_use_c, key="convert_c")

        with conversion_optcols[2]:
            conversion_use_pad = st.checkbox("Pad vocab, --pad-vocab", key="convert_pad")

        with conversion_optcols[3]:
            conversion_use_skip = st.checkbox("Skip unknown, --skip-unknown", key="convert_skip")

# Imatrix
# TODO
if imatrix:
    st.write("----")
    st.markdown("### Imatrix Creation")
    if convert:
        num_selected_high_precision = sum(1 for value in conversion_options.values() if value)
        if num_selected_high_precision == 0:
            st.error('Please select at least one high precision conversion option, or deselect the "Convert" option.')
        elif num_selected_high_precision == 1:
            for option, selected in conversion_options.items():
                if selected:
                    imatrix_selected_gguf_file = get_high_precision_outfile(convert_model_folder, option)
        else:
            high_precision_gguf_files = [get_high_precision_outfile(convert_model_folder, option) for option, selected in conversion_options.items() if selected]
            imatrix_selected_gguf_file = st.selectbox("Select a high precision GGUF file to be created", high_precision_gguf_files, key="imatrix_select_gguf_multiple")
    else:
        high_precision_gguf_files = list_gguf_files()
        imatrix_selected_gguf_file = st.selectbox("Select a high precision GGUF File", high_precision_gguf_files, key="imatrix_select_gguf")

    data_files = list_data_files()
    selected_data_file = st.selectbox("Select training data", data_files, key="imatrix_select_data")

    with st.expander("Options/flags for imatrix creation"):
        imatrix_optcols = st.columns(4)

        with imatrix_optcols[0]:
            imatrix_use_c = st.checkbox("Change context length", key="imatrix_use_c")
            imatrix_c = st.number_input("Size of the prompt context, -c", value=512, disabled=not imatrix_use_c, key="imatrix_c")

        with imatrix_optcols[1]:
            imatrix_use_b = st.checkbox("Change processing batch size", key="imatrix_use_b")
            imatrix_b = st.number_input("Logical maximum batch size, -b", value=2048, disabled=not imatrix_use_b, key="imatrix_b")

        with imatrix_optcols[2]:
            # only activate the ngl field if this box is checked
            imatrix_use_ngl = st.checkbox("Use GPU offloading", key="imatrix_use_ngl")
            imatrix_ngl = st.number_input("Number of GPU offloaded layers, -ngl", value=0, disabled=not imatrix_use_ngl, key="imatrix_ngl")

        with imatrix_optcols[3]:
            imatrix_use_t = st.checkbox("Change thread count", key="imatrix_use_t")
            imatrix_t = st.number_input("Number of threads to use, -t", value=4, disabled=not imatrix_use_t, key="imatrix_t")

# Quantize
# TODO
if quantize:
    st.write("----")
    st.markdown("### Quantize GGUF")
    if convert:
        num_selected_high_precision = sum(1 for value in conversion_options.values() if value)
        if num_selected_high_precision == 0:
            st.error('Please select at least one high precision conversion option, or deselect the "Convert" option.')
        elif num_selected_high_precision == 1:
            for option, selected in conversion_options.items():
                if selected:
                    quantize_selected_gguf_file = get_high_precision_outfile(convert_model_folder, option)
                    # TODO rework get_high_precision_oufile when you bring trigger_commands over
        else:
            high_precision_gguf_files = [get_high_precision_outfile(convert_model_folder, option) for option, selected in conversion_options.items() if selected]
            quantize_selected_gguf_file = st.selectbox("Select a high precision GGUF file to be created", high_precision_gguf_files, key="quantize_select_gguf_multiple")
    else:
        high_precision_gguf_files = list_gguf_files()
        quantize_selected_gguf_file = st.selectbox("Select a high precision GGUF File", high_precision_gguf_files, key="quantize_select_gguf")

    icol, kcol, lcol = st.columns(3)
    with icol:
        st.markdown("### I-Quants")
        ioptions = {option: st.checkbox(label=option, key=f"i_quantize_{option}") for option in config['quantization_I']}

    with kcol:
        st.markdown("### K-Quants")
        koptions = {option: st.checkbox(label=option, key=f"k_quantize_{option}") for option in config['quantization_K']}
        
    with lcol:
        st.markdown("### Legacy Quants")
        legacy_options = {option: st.checkbox(label=option, key=f"legacy_quantize_{option}") for option in config['quantization_legacy']}

    with st.expander("Options/parameters for quantization"):
        quantize_optcols = st.columns(2)

        with quantize_optcols[0]:
            quantize_use_imatrix = st.checkbox("Use importance matrix, --imatrix", key="quantize_imatrix")
            if imatrix:
                # TODO make it automatically determine the imatrix file
                # TODO likewise rework it when you bring over trigger_commands
                pass
            else:
                imatrix_files = list_imatrix_files()
                # TODO the disabling is not working properly
                selected_imatrix = st.selectbox("Select imatrix file", imatrix_files, disabled=not quantize_use_imatrix, key="quantize_select_imatrix")

        with quantize_optcols[1]:
            quantize_use_nthreads = st.checkbox("Change thread count", key="quantize_use_t")
            quantize_t = st.number_input("Number of threads to use, -nthreads", value=4, disabled=not quantize_use_nthreads, key="quantize_t")

# Upload
# TODO
if upload:
    st.write("----")
    st.markdown("### Upload to HuggingFace")
    if quantize or convert:
        # make it automatically determine the quantized file, hp or mp
        st.markdown("Placeholder - QorC")
    else:
        # give the user to choose a local quantized folder, hp or mp
        st.markdown("Placeholder - NQorC")
    # still need like token and such
    st.markdown("Placeholder")

if st.button("Queue All"):
    # manage logic to block queueing if input is bad
    # manage logic to queue the correct steps
    pass