# Last updated v0.2.0-pre2
# IMPORTS --------------------------------------------------------------------
import streamlit as st, importlib, json
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.paths import *
from util.finetune_parser import *
from util.scheduler import *
from transformers.trainer_utils import SchedulerType
from st_input_slider import st_input_slider
from peft.utils import SAFETENSORS_WEIGHTS_NAME, WEIGHTS_NAME
from collections import defaultdict

# want to load these things directly from llamafactory so it updates with the package
lf_constants = importlib.import_module("LLaMA-Factory.src.llmtuner.extras.constants")
lf_template = importlib.import_module("LLaMA-Factory.src.llmtuner.data.template")

# FUNCTIONS ------------------------------------------------------------------

# taken from LLaMA-Factory/src/llmtuner/webui/common.py
def load_dataset_info(dataset_dir: str):
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

# likewise see above
def list_adapters(model_name: str, finetuning_type: str):
    if finetuning_type not in getattr(lf_constants, "PEFT_METHODS"):
        return []

    adapters = []
    if model_name and finetuning_type == "lora":
        sav_dir = save_dir(model_name, finetuning_type)
        if sav_dir and os.path.isdir(sav_dir):
            for adapter in os.listdir(sav_dir):
                if os.path.isdir(os.path.join(sav_dir, adapter)) and any(
                    os.path.isfile(os.path.join(sav_dir, adapter, name)) for name in {WEIGHTS_NAME, SAFETENSORS_WEIGHTS_NAME}
                ):
                    adapters.append(adapter)
    return adapters



# UI CODE --------------------------------------------------------------------

add_indentation()

st.title("Finetuning with LLaMA-Factory")

# kinda copying llamaboard gui

# top row: model selection
model_cols = st.columns(3)

with model_cols[0]:
    available_models = list(getattr(lf_constants, "SUPPORTED_MODELS").keys()) + ["Custom"]
    model_name = st.selectbox("Model", available_models)

with model_cols[1]:
    model_path = st.text_input("Model path", value="")
    st.caption("Path to pretrained model or model identifier from Hugging Face.")

with model_cols[2]:
    adapter_path = st.selectbox("Adapter path", list_adapters(model_name, "lora"))

# TODO maybe at some point add finetuning method/adapter path but for now just lora is fine

# next row: advanced configs
with st.expander("Advanced configurations"):
    advanced_cols = st.columns(4)
    with advanced_cols[0]:
        quantization_bit = st.selectbox("Quantization Bit", ["none", "8", "4"]) # default none
        st.caption("Enable 4/8 bit model quantization (QLoRA).")
    
    with advanced_cols[1]:
        template = st.selectbox("Template", ["default"] + list(getattr(lf_template, "templates").keys())) # default default
        st.caption("The template used in constructing prompts.")
    
    with advanced_cols[2]:
        rope_scaling = st.radio("ROPE Scaling", ["none", "linear", "dynamic"], horizontal=True) # default none
    
    with advanced_cols[3]:
        booster = st.radio("Booster", ["none", "flashattn", "unsloth"], horizontal=True) # default none

# begin train tab
# first row: stage and data
data_cols = st.columns([25, 25, 50])
with data_cols[0]:
    stage = st.selectbox("Stage", getattr(lf_constants, "TRAINING_STAGES"))
    st.caption("The stage to perform in training.")

with data_cols[1]:
    dataset_dir = st.text_input("Data dir", value=data_dir())
    st.caption("Path to the data directory.")

with data_cols[2]:
    datasets = st.multiselect("Datasets", list_dataset(dataset_dir=dataset_dir, training_stage=stage))

st.divider()

# second row: learning rate, epochs, max gradient norm, max samples, compute type
second_row_cols = st.columns(5)
with second_row_cols[0]:
    lr = st.text_input("Learning rate", value=5e-5)
    st.caption("Initial learning rate for AdamW.")

with second_row_cols[1]:
    epochs = st.number_input("Epochs", value=3.0)
    st.caption("Total number of training epochs to perform.")

with second_row_cols[2]:
    max_grad_norm = st.number_input("Maximum gradient norm", value=1.0)
    st.caption("Norm for gradient clipping.")

with second_row_cols[3]:
    max_samples = st.number_input("Max samples", value=100000)
    st.caption("Maximum samples per dataset.")

with second_row_cols[4]:
    compute_type = st.selectbox("Compute type", ["fp16", "bf16", "fp32", "pure_bf16"])
    st.caption("Whether to use mixed precision training.")

st.divider()


# third row: cutoff length, batch size, gradient accumulation, val size, LR scheduler
third_row_cols = st.columns(5)
with third_row_cols[0]:
    cutoff_length = st_input_slider("Cutoff length", min_value=4, max_value=16384, step=1, value=1024, options={"marks": True})
    st.caption("Max tokens in input sequence.")

with third_row_cols[1]:
    batch_size = st_input_slider("Batch size", min_value=1, max_value=1024, step=1, value=2, options={"marks": True})
    st.caption("Number of samples processed on each GPU.")

with third_row_cols[2]:
    gradient_accumulation_steps = st_input_slider("Gradient accumulation", min_value=1, max_value=1024, step=1, value=8, options={"marks": True})
    st.caption("Number of steps for gradient accumulation.")

with third_row_cols[3]:
    val_size = st_input_slider("Val size", min_value=0.0, max_value=1.0, step=0.001, value=0.0, options={"marks": True})
    st.caption("Proportion of data in the dev set.")

with third_row_cols[4]:
    lr_scheduler_type = st.selectbox("LR scheduler", [scheduler.value for scheduler in SchedulerType], index=1)
    st.caption("Name of the learning rate scheduler.")


# extra configs dropdown
with st.expander("Extra configurations"):
    # first row: logging steps, save steps, warmup steps, NEFTune alpha, optimizer
    extra_configs_cols = st.columns(5)
    with extra_configs_cols[0]:
        logging_steps = st_input_slider("Logging steps", min_value=5, max_value=1000, step=5, value=5, options={"marks": True})
        st.caption("Number of steps between two logs.")

    with extra_configs_cols[1]:
        save_steps = st_input_slider("Save steps", min_value=10, max_value=5000, step=10, value=100, options={"marks": True})
        st.caption("Number of steps between two checkpoints.")

    with extra_configs_cols[2]:
        warmup_steps = st_input_slider("Warmup steps", min_value=0, max_value=5000, step=1, value=0, options={"marks": True})
        st.caption("Number of steps used for warmup.")

    with extra_configs_cols[3]:
        neftune_alpha = st_input_slider("NEFTune alpha", min_value=0.0, max_value=10.0, step=0.01, value=0.0, options={"marks": True})
        st.caption("Magnitude of noise adding to embedding vectors.")

    with extra_configs_cols[4]:
        optimizer = st.selectbox("Optimizer", ["adamw_torch", "adamw_8bit", "adafactor"])
        st.caption("The optimizer to use: adamw_torch, adamw_8bit, or adafactor.")

    st.divider()

    # second row: resize token embeddings/pack sequences, upcast layernorm/enable llama pro, enable S^2 attention/enable external logger
    extra_configs_cols2 = st.columns(3)
    with extra_configs_cols2[0]:
        resize_vocab = st.checkbox("Resize token embeddings", value=False)
        st.caption("Resize the tokenizer vocab and the embedding layers.")
        packing = st.checkbox("Pack sequences", value=False)
        st.caption("Pack sequences into samples of fixed length.")

    with extra_configs_cols2[1]:
        upcast_layernorm = st.checkbox("Upcast LayerNorm", value=False)
        st.caption("Upcast weights of layernorm in float32.")
        enable_llama_pro = st.checkbox("Enable LLaMA Pro", value=False)
        st.caption("Make the parameters in the expanded blocks trainable.")

    with extra_configs_cols2[2]:
        shift_attn = st.checkbox("Enable S^2 attention", value=False)
        st.caption("Use shift short attention proposed by LongLoRA.")
        report_to = st.checkbox("Enable external logger", value=False)
        st.caption("Use TensorBoard or wandb to log experiment.")

# TODO freeze tuning configs if you ever add freeze tuning
    
# lora configurations
with st.expander("LoRA configurations"):
    # first row: lora rank, lora alpha, lora dropout, lora+lr ratio, create new adapter
    lora_cols = st.columns(5)
    with lora_cols[0]:
        lora_rank = st_input_slider("LoRA rank", min_value=1, max_value=1024, step=1, value=8, options={"marks": True})
        st.caption("The rank of LoRA matrices.")

    with lora_cols[1]:
        lora_alpha = st_input_slider("LoRA alpha", min_value=1, max_value=2048, step=1, value=16, options={"marks": True})
        st.caption("LoRA scaling coefficient.")

    with lora_cols[2]:
        lora_dropout = st_input_slider("LoRA dropout", min_value=0.0, max_value=1.0, step=0.01, value=0.1, options={"marks": True})
        st.caption("Dropout ratio of LoRA weights.")

    with lora_cols[3]:
        loraplus_lr_ratio = st_input_slider("LoRA+LR ratio", min_value=0.0, max_value=64.0, step=0.01, value=0.0, options={"marks": True})
        st.caption("The LR ratio of the B matrices in LoRA.")

    with lora_cols[4]:
        create_new_adapter = st.checkbox("Create new adapter", value=False)
        st.caption("Create a new adapter with randomly initialized weight upon the existing one.")

    st.divider()
    
    # second row: use rslora/use dora, lora modules, additional modules
    lora_cols2 = st.columns(3)
    with lora_cols2[0]:
        use_rslora = st.checkbox("Use RSLora", value=False)
        st.caption("Use the rank stabilization scaling factor for LoRA layer.")
        use_dora = st.checkbox("Use DoRa", value=False)
        st.caption("Use weight-decomposed LoRA.")

    with lora_cols2[1]:
        lora_target = st.text_input("LoRA modules (optional)", value="")
        st.caption("Name(s) of modules to apply LoRA. Use commas to separate multiple modules.")
    
    with lora_cols2[2]:
        additional_target = st.text_input("Additional modules (optional)", value="")
        st.caption("Name(s) of modules apart from LoRA layers to be set as trainable. Use commas to separate multiple modules.")

# RLHF configurations
with st.expander("RLHF configurations"):
    # first row: dpo beta, dpo-ftx weight, orpo beta, reward model
    rlhf_cols = st.columns(4)
    with rlhf_cols[0]:
        dpo_beta = st_input_slider("DPO beta", min_value=0.0, max_value=1.0, step=0.01, value=0.1, options={"marks": True})
        st.caption("Value of the beta parameter in the DPO loss.")
    
    with rlhf_cols[1]:
        dpo_ftx = st_input_slider("DPO-FTX weight", min_value=0.0, max_value=10.0, step=0.01, value=0.0, options={"marks": True})
        st.caption("The weight of SFT loss in the DPO-ftx.")

    with rlhf_cols[2]:
        orpo_beta = st_input_slider("ORPO beta", min_value=0.0, max_value=1.0, step=0.01, value=0.1, options={"marks": True})
        st.caption("Value of the beta parameter in the ORPO loss.")

    with rlhf_cols[3]:
        reward_model = st.selectbox("Reward model", list_adapters(model_name=model_name, finetuning_type=stage), index=0)
        st.caption("Adapter of the reward model for PPO training.")

# galore configurations
with st.expander("GaLore configurations"):
    # first row: use galore, galore rank, update interval, galore scale, galore modules
    galore_cols = st.columns(5)
    with galore_cols[0]:
        use_galore = st.checkbox("Use GaLore", value=False)
        st.caption("Enable gradient low-Rank projection.")

    with galore_cols[1]:
        galore_rank = st_input_slider("GaLore rank", min_value=1, max_value=1024, step=1, value=16, options={"marks": True})
        st.caption("The rank of GaLore gradients.")

    with galore_cols[2]:
        update_interval = st_input_slider("Update interval", min_value=1, max_value=1024, step=1, value=200, options={"marks": True})
        st.caption("Number of steps to update the GaLore projection.")

    with galore_cols[3]:
        galore_scale = st_input_slider("GaLore scale", min_value=0.0, max_value=1.0, step=0.01, value=0.25, options={"marks": True})
        st.caption("GaLore scaling coefficient.")

    with galore_cols[4]:
        galore_target = st.text_input("GaLore modules", value="")
        st.caption("Name(s) of modules to apply GaLore. Use commas to separate multiple modules.")

button_cols = st.columns(5)
with button_cols[0]:
    output_dir = st.text_input("Output dir", value=get_timestamp())
    st.caption("Directory for saving results.")

with button_cols[1]:
    if st.button("Preview command", use_container_width=True):
        # TODO block if fields empty
        st.markdown(gen_cmd(parse_train_args(model_name, model_path, adapter_path, quantization_bit, 
                      template, rope_scaling, booster, stage, dataset_dir, datasets, 
                      lr, epochs, max_grad_norm, max_samples, compute_type, cutoff_length, 
                      batch_size, gradient_accumulation_steps, val_size, lr_scheduler_type, 
                      logging_steps, save_steps, warmup_steps,  neftune_alpha, optimizer,
                      resize_vocab, packing, upcast_layernorm, enable_llama_pro, shift_attn,
                      report_to, lora_rank, lora_alpha, lora_dropout, loraplus_lr_ratio,
                      create_new_adapter, use_rslora, use_dora, lora_target, additional_target,
                      dpo_beta, dpo_ftx, orpo_beta, reward_model, use_galore, galore_rank,
                      update_interval, galore_scale, galore_target, output_dir)))

with button_cols[2]:
    if st.button("Queue job", use_container_width=True):
        # TODO block if fields empty
        get_scheduler().add_job(queue_command(parse_train_args(model_name, model_path, adapter_path, quantization_bit, 
                      template, rope_scaling, booster, stage, dataset_dir, datasets, 
                      lr, epochs, max_grad_norm, max_samples, compute_type, cutoff_length, 
                      batch_size, gradient_accumulation_steps, val_size, lr_scheduler_type, 
                      logging_steps, save_steps, warmup_steps,  neftune_alpha, optimizer,
                      resize_vocab, packing, upcast_layernorm, enable_llama_pro, shift_attn,
                      report_to, lora_rank, lora_alpha, lora_dropout, loraplus_lr_ratio,
                      create_new_adapter, use_rslora, use_dora, lora_target, additional_target,
                      dpo_beta, dpo_ftx, orpo_beta, reward_model, use_galore, galore_rank,
                      update_interval, galore_scale, galore_target, output_dir)))

with button_cols[3]:
    st.button("Save arguments", use_container_width=True, disabled=True) # TODO implement

with button_cols[4]:
    st.button("Load arguments", use_container_width=True, disabled=True) # TODO implement