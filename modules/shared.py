# shared.py

# Shared configuration data
shared = {
    'checkbox_high_options': ["Q8_0", "F16", "F32"],
    'checkbox_options': [
        "IQ2_XXS", "IQ2_XS", "IQ3_XXS", "Q2_K", "Q2_K_S", "Q3_K_XS", "Q3_K_S", "Q3_K_M", "Q3_K_L",
        "Q4_0", "Q4_1", "Q4_K_S", "Q4_K_M", "Q5_0", "Q5_1", "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0", "F16", "F32"
    ],
}


# Separate variable for module imports
modules_to_import = {
    "downloading_models": ["show_downloading_models_page"],
    "High_Precision_Quantization": ["show_high_precision_quantization_page"],
    "Medium_Precision_Quantization": ["show_medium_precision_quantization_page"],
    "UploadtoHuggingface": ["show_model_management_page"],
    "token_encrypt": ["show_token_encrypt_page"],
}