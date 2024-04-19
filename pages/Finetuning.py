# Last updated v0.2.0-pre1
# IMPORTS --------------------------------------------------------------------
import streamlit as st, importlib, json
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.paths import *
from typing import Dict, Any
from transformers.trainer_utils import SchedulerType

# want to load these things directly from llamafactory so it updates with the package
lf_constants = importlib.import_module("LLaMA-Factory.src.llmtuner.extras.constants")
lf_template = importlib.import_module("LLaMA-Factory.src.llmtuner.data.template")

# FUNCTIONS ------------------------------------------------------------------

# taken from LLaMA-Factory/src/llmtuner/webui/common.py
def load_dataset_info(dataset_dir: str) -> Dict[str, Dict[str, Any]]:
    DATA_CONFIG = getattr(lf_constants, "DATA_CONFIG")
    try:
        with open(os.path.join(dataset_dir, DATA_CONFIG), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as err:
        print("Cannot open {} due to {}.".format(os.path.join(dataset_dir, DATA_CONFIG), str(err)))
        return {}

# likewise see above
def list_dataset(dataset_dir: str = None, training_stage: str = list(getattr(lf_constants, "TRAINING_STAGES").keys())[0]):
    dataset_info = load_dataset_info(dataset_dir if dataset_dir is not None else getattr(lf_constants, "DEFAULT_DATA_DIR"))
    ranking = getattr(lf_constants, "TRAINING_STAGES")[training_stage] in getattr(lf_constants, "STAGES_USE_PAIR_DATA")
    datasets = [k for k, v in dataset_info.items() if v.get("ranking", False) == ranking]
    return datasets

# UI CODE --------------------------------------------------------------------

add_indentation()

st.title("Finetuning with LLaMA-Factory")

# kinda copying llamaboard gui

# top row: model selection
model_cols = st.columns(2)

with model_cols[0]:
    available_models = list(getattr(lf_constants, "SUPPORTED_MODELS").keys()) + ["Custom"]
    model_name = st.selectbox("Model", available_models)

with model_cols[1]:
    model_path = st.text_input("Model Path: local (relative to user/models) or HuggingFace Hub", value="")

# TODO maybe at some point add finetuning method/adapter path but for now just lora is fine

# next row: advanced configs
with st.expander("Advanced configurations"):
    advanced_cols = st.columns(4)
    with advanced_cols[0]:
        quantization_bit = st.selectbox("Quantization Bit", ["none", "8", "4"]) # default none
    
    with advanced_cols[1]:
        template = st.selectbox("Template", list(getattr(lf_template, "templates").keys())) # default default
    
    with advanced_cols[2]:
        rope_scaling = st.radio("ROPE Scaling", ["none", "linear", "dynamic"], horizontal=True) # default none
    
    with advanced_cols[3]:
        booster = st.radio("Booster", ["none", "flashattn", "unsloth"], horizontal=True) # default none

# begin train tab
# first row: stage and data
data_cols = st.columns([25, 25, 50])
with data_cols[0]:
    stage = st.selectbox("Stage", getattr(lf_constants, "TRAINING_STAGES"))

with data_cols[1]:
    data_path = st.text_input("Data dir", value=data_dir())

with data_cols[2]:
    datasets = st.multiselect("Datasets", list_dataset(dataset_dir=data_path, training_stage=stage))

# second row: learning rate, epochs, max gradient norm, max samples, compute type
second_row_cols = st.columns(5)
with second_row_cols[0]:
    lr = st.text_input("Learning rate", value=5e-5)

with second_row_cols[1]:
    epochs = st.number_input("Epochs", value=3.0)

with second_row_cols[2]:
    max_grad_norm = st.number_input("Maximum gradient norm", value=1.0)

with second_row_cols[3]:
    max_samples = st.number_input("Max samples", value=100000)

with second_row_cols[4]:
    compute_type = st.selectbox("Compute type", ["fp16", "bf16", "fp32", "pure_bf16"], horizontal=True)


# third row: cutoff length, batch size, gradient accumulation, val size, LR scheduler
third_row_cols = st.columns(5)
with third_row_cols[0]:
    cutoff_length = st.slider("Cutoff length", min_value=4, max_value=16384, step=1, value=1024)

with third_row_cols[1]:
    batch_size = st.slider("Batch size", min_value=1, max_value=1024, step=1, value=2)

with third_row_cols[2]:
    gradient_accumulation_steps = st.slider("Gradient accumulation", min_value=1, max_value=1024, step=1, value=8)

with third_row_cols[3]:
    val_size = st.slider("Val size", min_value=0.0, max_value=1.0, step=0.001, value=0)

with third_row_cols[4]:
    optimizer = st.selectbox("LR scheduler", [scheduler.value for scheduler in SchedulerType])


# extra configs dropdown
with st.expander("Extra configurations"):
    # first row: logging steps, save steps, warmup steps, NEFTune alpha, optimizer
    extra_configs_cols = st.columns(5)
    with extra_configs_cols[0]:
        logging_steps = st.slider("Logging steps", min_value=5, max_value=1000, step=5, value=5)

    with extra_configs_cols[1]:
        save_steps = st.slider("Save steps", min_value=10, max_value=5000, step=10, value=100)

    with extra_configs_cols[2]:
        warmup_steps = st.slider("Warmup steps", min_value=0, max_value=5000, step=1, value=0)

    with extra_configs_cols[3]:
        neftune_alpha = st.slider("NEFTune alpha", min_value=0, max_value=10, step=0.01, value=0)

    with extra_configs_cols[4]:
        optimizer = st.selectbox("Optimizer", ["adamw_torch", "adamw_8bit", "adafactor"])

    # second row: resize token embeddings/pack sequences, upcast layernorm/enable llama pro, enable S^2 attention/enable external logger
    extra_configs_cols2 = st.columns(3)
    with extra_configs_cols2[0]:
        resize_vocab = st.checkbox("Resize token embeddings", value=False)
        packing = st.checkbox("Pack sequences", value=False)

    with extra_configs_cols2[1]:
        upcast_layernorm = st.checkbox("Upcast layernorm", value=False)
        enable_llama_pro = st.checkbox("Enable LLaMA Pro", value=False)

    with extra_configs_cols2[2]:
        shift_attn = st.checkbox("Enable S^2 attention", value=False)
        report_to = st.checkbox("Enable external logger", value=False)

# TODO freeze tuning configs if you ever add freeze tuning
    
# lora configurations
with st.expander("LoRA configurations"):
    # first row: lora rank, lora alpha, lora dropout, lora+lr ratio, create new adapter
    lora_cols = st.columns(5)
    with lora_cols[0]:
        lora_rank = st.slider("LoRA rank", min_value=1, max_value=1024, step=1, value=8)

    with lora_cols[1]:
        lora_alpha = st.slider("LoRA alpha", min_value=1, max_value=2048, step=1, value=16)

    with lora_cols[2]:
        lora_dropout = st.slider("LoRA dropout", min_value=0, max_value=1, step=0.01, value=0.1)

    with lora_cols[3]:
        loraplus_lr_ratio = st.slider("LoRA+LR ratio", min_value=0, max_value=64, step=0.01, value=0)

    with lora_cols[4]:
        create_new_adapter = st.checkbox("Create new adapter", value=False)
    
    # second row: use rslora/use dora, lora modules, additional modules
    lora_cols2 = st.columns(3)
    with lora_cols2[0]:
        use_rslora = st.checkbox("Use RSLora", value=False)
        use_dora = st.checkbox("Use DoRa", value=False)

    lora_target = st.text_input("LoRA target", value="")
    additional_target = st.text_input("Additional target", value="")

# RLHF configurations
with st.expander("RLHF configurations"):
    # first row: dpo beta, dpo-ftx weight, orpo beta, reward model
    rlhf_cols = st.columns(4)
    with rlhf_cols[0]:
        dpo_beta = st.slider("DPO beta", min_value=0, max_value=1, step=0.01, value=0.1)
    
    with rlhf_cols[1]:
        dpo_ftx = st.slider("DPO-FTX weight", min_value=0, max_value=10, step=0.01, value=0)

    with rlhf_cols[2]:
        orpo_beta = st.slider("ORPO beta", min_value=0, max_value=1, step=0.01, value=0.1)

    with rlhf_cols[3]:
        # TODO add reward model adapter path
        reward_model = st.selectbox("Reward model", None, index=0)

# galore configurations
with st.expander("GaLore configurations"):
    # first row: use galore, galore rank, update interval, galore scale, galore modules
    galore_cols = st.columns(5)
    with galore_cols[0]:
        use_galore = st.checkbox("Use GaLore", value=False)

    with galore_cols[1]:
        galore_rank = st.slider("GaLore rank", min_value=1, max_value=1024, step=1, value=16)

    with galore_cols[2]:
        update_interval = st.slider("Update interval", min_value=1, max_value=1024, step=1, value=200)

    with galore_cols[3]:
        galore_scale = st.slider("GaLore scale", min_value=0, max_value=1, step=0.01, value=0.25)

    with galore_cols[4]:
        galore_target = st.text_input("GaLore target", value="")


# buttons: preview command, queue job, set output dir or something, save and load arguments
# TODO implement all of these
button_cols = st.columns(5)
with button_cols[0]:
    st.button("Preview command")

with button_cols[1]:
    st.button("Queue job")


with button_cols[2]:
    st.button("Save arguments")

with button_cols[3]:
    st.button("Load arguments")

# TODO output dir, config path