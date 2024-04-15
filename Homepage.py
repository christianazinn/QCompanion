# main.py
import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title, add_indentation

# UI CODE ---------------------------------------------------------------------------------

show_pages(
    [
    Page("Homepage.py", "Home", ":house:"),
    Page("pages/Docs.py", "Docs", ":books:"),
    Section("Manually convert models", icon=":arrows_counterclockwise:"),
    Page("pages/Hugging_Face_Downloader.py", "Download model", ":inbox_tray:"),
    Page("pages/Convert_Safetensors.py", "Convert Safetensors to High Precision", ":gem:"),
    Page("pages/Create_IMatrix.py", "Create Importance Matrix", ":chart_with_upwards_trend:"),
    Page("pages/Quantize_GGUF.py", "Quantize GGUF", ":heavy_plus_sign:" ),
    Page("pages/Upload_Converted_To_HF.py", "Upload model to HuggingFace", ":outbox_tray:"),
    Page("pages/Queue_GUI.py", "Queue GUI", ":inbox_tray:"),
    Section("Extra Tools", icon=":toolbox:"),
    Page("pages/HF_Token_Encrypter.py", "Security", ":lock:"),
    ]    
)

add_indentation()



st.markdown(""" 
# Welcome to Ollama-Companion.  
---
Thank you for installing the Ollama-Companion, to get started use the sidebar to navigate to the page you want to use,  
if you have any question sor want to learn how to use a certain functionality then navigate to the ***"Docs"*** page located within the sidebar.""")

