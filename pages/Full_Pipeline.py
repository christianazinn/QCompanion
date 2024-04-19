# Last updated v0.1.3
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.constants import config
from util.scheduler import *
from util.paths import *
from util.utils import *
from util.key import decrypt_token

# FUNCTIONS ---------------------------------------------------------------------------------

# Download scheduler
def trigger_download(model_name):
    command = ["python3", "util/download.py", model_name]
    get_scheduler().add_job(command)

# Convert scheduler
def trigger_convert(model_folder, options, vocab, ctx, pad, skip):
    for option, selected in options.items():
        if selected:
            outfile = f"{model_folder}-{option.lower()}.GGUF"
            script_path = llama_cpp_dir() / "convert.py"

            command = [
                "python3", str(script_path),
                str(models_dir() / model_folder),
                "--outfile", str(get_high_precision_outdir(model_folder) / outfile),
                "--outtype", option.lower()
            ]

            if vocab:
                command.extend(["--vocabtype", vocab])

            if ctx:
                command.extend(["--ctx", str(ctx)])

            if pad:
                command.append("--pad-vocab")

            if skip:
                command.append("--skip-unknown")

            get_scheduler().add_job(command)

# Imatrix scheduler
def trigger_imatrix(gguf_base, data, c, b, ngl, t):
    outfile = get_imatrix_filepath(gguf_base, data)
    data_path = imatrix_data_dir() / data
    # gguf_base IS model_path

    command = ["llama.cpp/imatrix", "-m", str(gguf_base), "-f", str(data_path), "-o", str(outfile), "--verbosity", "2",
               "-c", str(c), "-b", str(b)]
    
    if ngl:
        command.extend(["-ngl", str(ngl)])

    if t:
        command.extend(["-t", str(t)])

    get_scheduler().add_job(command)


# Quantize scheduler
def trigger_quantize(model_path, options, imatrix, nthreads):
    # source_path IS model_path
    gguf_path = Path(model_path)
    med_precision_outdir = get_med_precision_outdir(gguf_path.parts[-3])
    for option, selected in options.items():
        if selected:
            modified_model_file = modify_model_file(gguf_path.name.lower())
            output_path = med_precision_outdir / f"{modified_model_file}-{option.upper()}.GGUF"

            command = [str(llama_cpp_dir() / 'quantize'), "--allow-requantize", str(model_path), str(output_path), option]

            if imatrix:
                command.insert(1, "--imatrix")
                command.insert(2, str(imatrix))

            if nthreads:
                command.extend([str(nthreads)])

            get_scheduler().add_job(command)

# Upload scheduler
# unlike the others you HAVE to provide files_to_upload as a list of FILE NAMES not PATHS
def trigger_upload(token, repo_name, files_to_upload, high_precision_files, medium_precision_files, selected_model):
    
    final_upload = []

    # Rename particular filepaths
    for file_name in files_to_upload:
        if file_name in high_precision_files.get(selected_model, []):
            folder_path = get_high_precision_outdir(selected_model)
        elif file_name in medium_precision_files.get(selected_model, []):
            folder_path = get_med_precision_outdir(selected_model)
        else:
            continue

        file_path = folder_path / file_name
        final_upload.append(str(file_path))

    command = ["python3", "util/upload.py", token, repo_name, *final_upload]
    get_scheduler().add_job(command)

# Autoupload scheduler
# Here you have to provide the selected_files_hp and selected_files_mp as a list of PATHS
def trigger_upload_auto(token, repo_name, selected_files_hp, selected_files_mp):
    final_upload = [file for file in selected_files_hp + selected_files_mp]
    command = ["python3", "util/upload.py", token, repo_name, *final_upload]
    get_scheduler().add_job(command)

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
if download:
    st.write("----")
    st.markdown("### Download from HuggingFace")
    model_name = st.text_input("Download Safetensors format models from Huggingface", "Model_Creator/Model_Name")
    if st.button("Get File List"):
        _, file_links = get_files_from_repo(f"https://huggingface.co/api/models/{model_name}/tree/main", model_name)
        if file_links:
            st.session_state['model_name'] = model_name
            files_info = "\n".join(f"{name}, Size: {size}" for name, size in file_links.items())
            st.text_area("Files Information", files_info, height=300)
        else:
            st.error("Unable to retrieve file links.")
            if 'model_name' in st.session_state:
                del st.session_state['model_name']
else: # if download is not selected, remove the file_links_dict and model_name from the session state
    if 'model_name' in st.session_state:
        del st.session_state['model_name']

# Convert
if convert:
    st.write("----")
    st.markdown("### Convert Safetensors to High Precision")
    if download: # automatically determine where download.py will download it
        if 'model_name' in st.session_state:
            convert_model_folder = st.session_state['model_name'].split("/")[1]
            st.markdown(f"Using to-be-created model directory `{models_dir() / convert_model_folder}`")
        else:
            st.error("Please choose a model to download first.")
            convert_model_folder = None
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
if imatrix:
    st.write("----")
    st.markdown("### Imatrix Creation")
    if convert:
        num_selected_high_precision = sum(1 for value in conversion_options.values() if value)
        if num_selected_high_precision == 0:
            st.error('Please select at least one high precision conversion option, or deselect the "Convert" option.')
            imatrix_selected_gguf_file = None
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

    data_files = list_imatrix_data_files()
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
if quantize:
    st.write("----")
    st.markdown("### Quantize GGUF")
    if convert:
        num_selected_high_precision = sum(1 for value in conversion_options.values() if value)
        if num_selected_high_precision == 0:
            st.error('Please select at least one high precision conversion option, or deselect the "Convert" option.')
            quantize_selected_gguf_file = None
        elif num_selected_high_precision == 1:
            for option, selected in conversion_options.items():
                if selected:
                    quantize_selected_gguf_file = get_high_precision_outfile(convert_model_folder, option)
        else:
            high_precision_gguf_files = [get_high_precision_outfile(convert_model_folder, option) for option, selected in conversion_options.items() if selected]
            quantize_selected_gguf_file = st.selectbox("Select a high precision GGUF file to be quantized from", high_precision_gguf_files, key="quantize_select_gguf_multiple")
    else:
        high_precision_gguf_files = list_gguf_files()
        quantize_selected_gguf_file = st.selectbox("Select a high precision GGUF file to be quantized from", high_precision_gguf_files, key="quantize_select_gguf")

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
                if not imatrix_selected_gguf_file:
                    st.error("Please select a high precision GGUF file for the to-be-created importance matrix first.")
                if not selected_data_file:
                    st.error("Please select training data for the to-be-created importance matrix first.")
                if imatrix_selected_gguf_file and selected_data_file:
                    selected_imatrix = get_imatrix_filepath(imatrix_selected_gguf_file, selected_data_file)
            else:
                imatrix_files = list_imatrix_files()
                selected_imatrix = st.selectbox("Select imatrix file", imatrix_files, disabled=not quantize_use_imatrix, key="quantize_select_imatrix")

        with quantize_optcols[1]:
            quantize_use_nthreads = st.checkbox("Change thread count", key="quantize_use_t")
            quantize_t = st.number_input("Number of threads to use, -nthreads", value=4, disabled=not quantize_use_nthreads, key="quantize_t")

# Upload
if upload:
    high_precision_files = list_model_files("High-Precision-Quantization")
    medium_precision_files = list_model_files("Medium-Precision-Quantization")
    
    st.write("----")
    st.markdown("### Upload to HuggingFace")
    if quantize or convert:
        selected_files_hp = []
        selected_files_mp = []
        if convert:
            # determine all high precision files
            for option, selected in conversion_options.items():
                if selected:
                    selected_files_hp.append(get_high_precision_outfile(convert_model_folder, option))
        if quantize:
            # determine all medium precision files
            for option, selected in (ioptions | koptions | legacy_options).items():
                if selected:
                    selected_files_mp.append(get_med_precision_outfile(Path(quantize_selected_gguf_file).name, option))

            # TODO maybe allow the user to select which of the resulting files to upload?
            # TODO for the future: upload imatrix, upload README automatically, upload whole directory at once
    else:
        # Select another model
        all_models = list(set(high_precision_files.keys()) | set(medium_precision_files.keys()))
        selected_model = st.selectbox("Select a Model", all_models, index=0)

        # File selection multiselect
        combined_files = high_precision_files.get(selected_model, []) + medium_precision_files.get(selected_model, [])
        selected_files = st.multiselect("Select Files to Upload", combined_files, key="file_selector")

    # Repository details and README content
    repo_name = st.text_input("Repository Name", value="Repository Name")

    # Token input
    use_unencrypted_token = st.checkbox("Unencrypted Token")
    if use_unencrypted_token:
        hf_token = st.text_input("Hugging Face Token", type="password")
    else:
        encrypted_token = st.text_input("Enter Encrypted Token", type="password")
        if encrypted_token:
            hf_token = decrypt_token(encrypted_token)
        else:
            hf_token = None

# QUEUE IT ALLLLLLLLLLLLLL --------------------------------------------------------------

if st.button("Queue All"):

    valid = True

    # manage logic to block queueing if input is bad
    # this has to happen first before anything gets queued
    if download:
        if not 'model_name' in st.session_state:
            st.error("Please choose a model to download first.")
            valid = False
    if convert:
        # this can actually happen because of how finnicky session state is
        if not convert_model_folder and 'model_name' in st.session_state:
            st.error("Please choose a model to download first.")
            valid = False
        if not any(conversion_options.values()):
            st.error("Please select at least one quantization type before running commands.")
            valid = False
    if imatrix:
        if not imatrix_selected_gguf_file:
            st.error("Please select a high precision GGUF file for the to-be-created importance matrix first.")
            valid = False
        if not selected_data_file:
            st.error("Please select training data for the to-be-created importance matrix first.")
            valid = False
    if quantize:
        if not quantize_selected_gguf_file:
            st.error("Please select a high precision GGUF file to be quantized from.")
            valid = False
        if not (any((ioptions | koptions | legacy_options).values())):
            st.error("Please select at least one quantization type before running commands.")
            valid = False
        if quantize_use_imatrix and not selected_imatrix:
            st.error("Please select an importance matrix file.")
            valid = False
    if upload:
        if not hf_token:
            st.error("Please provide a Hugging Face token.")
            valid = False
        if (quantize or convert) and not (selected_files_hp or selected_files_mp):
            st.error("Please quantize/convert files to upload.")
            valid = False
        if not (quantize or convert) and not selected_files:
            st.error("Please select files to upload.")
            valid = False

    # manage logic to queue the correct steps
    if valid:
        if download:
            trigger_download(model_name)
        if convert:
            trigger_convert(convert_model_folder, conversion_options, 
                            conversion_vocab if conversion_use_vocab else None, 
                            conversion_c if conversion_use_c else None, 
                            conversion_use_pad, conversion_use_skip)
        if imatrix:
            trigger_imatrix(imatrix_selected_gguf_file, selected_data_file, 
                            imatrix_c, imatrix_b, imatrix_ngl if imatrix_use_ngl else None, 
                            imatrix_t if imatrix_use_t else None)
        if quantize:
            trigger_quantize(quantize_selected_gguf_file, ioptions | koptions | legacy_options, 
                            selected_imatrix if quantize_use_imatrix else None, 
                            quantize_t if quantize_use_nthreads else None)
        if upload and (quantize or convert):
            trigger_upload_auto(hf_token, repo_name, selected_files_hp, selected_files_mp)
        elif upload:
            trigger_upload(hf_token, repo_name, selected_files, 
                            high_precision_files, medium_precision_files, selected_model)