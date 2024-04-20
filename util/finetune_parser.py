# Last updated v0.2.0-pre2
# IMPORTS ---------------------------------------------------------------------------------
import importlib, os, datetime
from typing import Any, Dict
from util.paths import cache_dir, save_dir, llamafactory_dir

lf_constants = importlib.import_module("LLaMA-Factory.src.llmtuner.extras.constants")

# FUNCTIONS ---------------------------------------------------------------------------------

def get_module(model_name: str) -> str:
    return getattr(lf_constants, "DEFAULT_MODULE").get(model_name.split("-")[0], "q_proj,v_proj")

# this is what actually formats it
def gen_cmd(args: Dict[str, Any]) -> str:
    args.pop("disable_tqdm", None)
    args["plot_loss"] = args.get("do_train", None)
    current_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    cmd_lines = ["CUDA_VISIBLE_DEVICES={} python src/train_bash.py ".format(current_devices)]
    for k, v in args.items():
        if v is not None and v is not False and v != "":
            cmd_lines.append("    --{} {} ".format(k, str(v)))
    cmd_text = "\\\n".join(cmd_lines)
    cmd_text = "```bash\n{}\n```".format(cmd_text)
    return cmd_text

# and this formats for the scheduler
def queue_command(args: Dict[str, Any]) -> str:
    args.pop("disable_tqdm", None)
    args["plot_loss"] = args.get("do_train", None)
    current_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    cmd_lines = [f"CUDA_VISIBLE_DEVICES={current_devices}", "python3", f"{llamafactory_dir()}/src/train_bash.py"]
    for k, v in args.items():
        if v is not None and v is not False and v != "":
            cmd_lines.extend([f"--{k}", str(v)])
    return cmd_lines

# YYYY-MM-DD--HH-MM-SS format
def get_timestamp() -> str:
    return "train_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# this is so efficient!!!
def parse_train_args(model_name, model_path, adapter_path, quantization_bit, 
                      template, rope_scaling, booster, stage, dataset_dir, datasets, 
                      lr, epochs, max_grad_norm, max_samples, compute_type, cutoff_length, 
                      batch_size, gradient_accumulation_steps, val_size, lr_scheduler_type, 
                      logging_steps, save_steps, warmup_steps,  neftune_alpha, optimizer,
                      resize_vocab, packing, upcast_layernorm, use_llama_pro, shift_attn,
                      report_to, lora_rank, lora_alpha, lora_dropout, loraplus_lr_ratio,
                      create_new_adapter, use_rslora, use_dora, lora_target, additional_target,
                      dpo_beta, dpo_ftx, orpo_beta, reward_model, use_galore, galore_rank,
                      update_interval, galore_scale, galore_target, output_dir):

    if adapter_path:
        adapter_name_or_path = ",".join([save_dir(model_name, "lora", adapter) for adapter in adapter_path])
    else:
        adapter_name_or_path = None

    args = dict(
        stage=getattr(lf_constants, "TRAINING_STAGES")[stage],
        do_train=True,
        model_name_or_path=model_path,
        adapter_name_or_path=adapter_name_or_path,
        cache_dir=cache_dir(),
        finetuning_type="lora",
        quantization_bit=int(quantization_bit) if quantization_bit in ["8", "4"] else None,
        template=template,
        rope_scaling=rope_scaling if rope_scaling in ["linear", "dynamic"] else None,
        flash_attn=(booster == "flashattn"),
        use_unsloth=(booster == "unsloth"),
        dataset_dir=dataset_dir,
        dataset=",".join(datasets),
        cutoff_len=cutoff_length,
        learning_rate=float(lr),
        num_train_epochs=float(epochs),
        max_samples=int(max_samples),
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        lr_scheduler_type=lr_scheduler_type,
        max_grad_norm=float(max_grad_norm),
        logging_steps=logging_steps,
        save_steps=save_steps,
        warmup_steps=warmup_steps,
        neftune_noise_alpha=neftune_alpha or None,
        optim=optimizer,
        resize_vocab=resize_vocab,
        packing=packing,
        upcast_layernorm=upcast_layernorm,
        use_llama_pro=use_llama_pro,
        shift_attn=shift_attn,
        report_to="all" if report_to else "none",
        use_galore=use_galore,
        output_dir=save_dir(model_name, "lora", output_dir),
        fp16=(compute_type == "fp16"),
        bf16=(compute_type == "bf16"),
        pure_bf16=(compute_type == "pure_bf16"),
    )
    args["disable_tqdm"] = True

    # if args["finetuning_type"] == "freeze":
    #     args["num_layer_trainable"] = get("train.num_layer_trainable")
    #     args["name_module_trainable"] = get("train.name_module_trainable")
    # elif args["finetuning_type"] == "lora":
    args["lora_rank"] = lora_rank
    args["lora_alpha"] = lora_alpha
    args["lora_dropout"] = lora_dropout
    args["loraplus_lr_ratio"] = loraplus_lr_ratio or None
    args["create_new_adapter"] = create_new_adapter
    args["use_rslora"] = use_rslora
    args["use_dora"] = use_dora
    args["lora_target"] = lora_target or get_module(model_name)
    args["additional_target"] = additional_target or None

    # TODO technically this is usable even without freeze finetuning but eh whatever
    # if args["use_llama_pro"]:
    #     args["num_layer_trainable"] = get("train.num_layer_trainable")

    if args["stage"] == "ppo":
        args["reward_model"] = ",".join([save_dir(model_name, "lora", adapter) for adapter in reward_model])
        args["reward_model_type"] = "lora" if args["finetuning_type"] == "lora" else "full"
    elif args["stage"] == "dpo":
        args["dpo_beta"] = dpo_beta
        args["dpo_ftx"] = dpo_ftx
    elif args["stage"] == "orpo":
        args["orpo_beta"] = orpo_beta

    if val_size > 1e-6 and args["stage"] != "ppo":
        args["val_size"] = val_size
        args["evaluation_strategy"] = "steps"
        args["eval_steps"] = args["save_steps"]
        args["per_device_eval_batch_size"] = args["per_device_train_batch_size"]
        args["load_best_model_at_end"] = args["stage"] not in ["rm", "ppo"]

    if args["use_galore"]:
        args["galore_rank"] = galore_rank
        args["galore_update_interval"] = update_interval
        args["galore_scale"] = galore_scale
        args["galore_target"] = galore_target

    return args

# TODO save/load args at some point - this will probably require every argument to be stored in session storage
"""
def save_args(self, data: Dict):
    config_dict: Dict[str, Any] = {}
    lang = data[self.manager.get_elem_by_id("top.lang")]
    config_path = data[self.manager.get_elem_by_id("train.config_path")]
    skip_ids = ["top.lang", "top.model_path", "train.output_dir", "train.config_path"]
    for elem, value in data.items():
        elem_id = self.manager.get_id_by_elem(elem)
        if elem_id not in skip_ids:
            config_dict[elem_id] = value

    save_path = save_args(config_path, config_dict)
    return {output_box: ALERTS["info_config_saved"][lang] + save_path}

def load_args(self, lang: str, config_path: str):
    config_dict = load_args(config_path)
    if config_dict is None:
        gr.Warning(ALERTS["err_config_not_found"][lang])
        return {output_box: ALERTS["err_config_not_found"][lang]}

    output_dict: Dict["Component", Any] = {output_box: ALERTS["info_config_loaded"][lang]}
    for elem_id, value in config_dict.items():
        output_dict[self.manager.get_elem_by_id(elem_id)] = value

    return output_dict
"""