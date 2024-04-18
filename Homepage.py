# main.py
# Version 0.1.3-pre1: First bits of full pipeline UI code
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import Page, Section, show_pages, add_indentation
from util.scheduler import *

# UI CODE ---------------------------------------------------------------------------------

show_pages(
    [
    Page("Homepage.py", "Home", ":house:"),
    Page("pages/Docs.py", "Docs", ":books:"),
    Section("Manually convert models", icon=":open_hands:"),
    Page("pages/Full_Pipeline.py", "Full Pipeline Queue", ":arrows_clockwise:"),
    Page("pages/Queue_GUI.py", "Queue GUI", ":arrows_counterclockwise:"),
    Section("Manually convert models - Legacy", icon=":cd:"),
    Page("pages/Hugging_Face_Downloader.py", "Download model", ":inbox_tray:"),
    Page("pages/Convert_Safetensors.py", "Safetensors to GGUF", ":gem:"),
    Page("pages/Create_IMatrix.py", "Create Importance Matrix", ":chart_with_upwards_trend:"),
    Page("pages/Quantize_GGUF.py", "Quantize GGUF", ":heavy_plus_sign:" ),
    Page("pages/Upload_Converted_To_HF.py", "Upload model to HuggingFace", ":outbox_tray:"),
    Section("Extra Tools", icon=":toolbox:"),
    Page("pages/HF_Token_Encrypter.py", "Security", ":lock:"),
    ]
)

add_indentation()

st.markdown(""" 
# Welcome to QCompanion.  
---
Thank you for installing QCompanion. To get started, use the sidebar to navigate to the page you want to use.  

If you have any questions or want to learn how to use a certain functionality, navigate to the ***"Docs"*** page located within the sidebar.""")

