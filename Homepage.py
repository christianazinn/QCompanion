# main.py
# Version 0.1.3-pre3: Refactor to use a unified queuer for all quantization pipeline tasks
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import Page, Section, show_pages, add_indentation
from util.scheduler import *

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

pages_to_show = [
    Page("Homepage.py", "Home", ":house:"),
    Page("pages/Docs.py", "Docs", ":books:"),
    Section("Manually convert models", icon=":open_hands:"),
    Page("pages/Full_Pipeline.py", "Full Pipeline Queue", ":arrows_clockwise:"),
    Page("pages/Queue_GUI.py", "Queue GUI", ":arrows_counterclockwise:"),
    Section("Extra Tools", icon=":toolbox:"),
    Page("pages/HF_Token_Encrypter.py", "Security", ":lock:"),
]

legacy_pages = [
    Page("pages/legacy/Hugging_Face_Downloader.py", "Legacy: Download model", ":inbox_tray:"),
    Page("pages/legacy/Convert_Safetensors.py", "Legacy: Safetensors to GGUF", ":gem:"),
    Page("pages/legacy/Create_IMatrix.py", "Legacy: Create Importance Matrix", ":chart_with_upwards_trend:"),
    Page("pages/legacy/Quantize_GGUF.py", "Legacy: Quantize GGUF", ":heavy_plus_sign:" ),
    Page("pages/legacy/Upload_Converted_To_HF.py", "Legacy: Upload model to HuggingFace", ":outbox_tray:")
]

st.markdown(""" 
# Welcome to QCompanion.  
---
Thank you for installing QCompanion. To get started, use the sidebar to navigate to the page you want to use.  

If you have any questions or want to learn how to use a certain functionality, navigate to the ***"Docs"*** page located within the sidebar.""")

show_legacy = st.checkbox("Show legacy pages", value=False)

show_pages(pages_to_show + legacy_pages if show_legacy else pages_to_show)

add_indentation()