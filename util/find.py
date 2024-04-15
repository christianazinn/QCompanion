import streamlit as st
from pathlib import Path

# find the 'llama.cpp/models' directory
@st.cache_data
def find_llama_models_dir(start_path, max_up=4, max_down=3):
    def search_upwards(path, depth):
        if depth > max_up:
            return None
        if (path / "llama.cpp/models").exists():
            return path / "llama.cpp/models"
        return search_upwards(path.parent, depth + 1)
    
    @st.cache_data
    def search_downwards(path, depth):
        if depth > max_down:
            return None
        if (path / "llama.cpp/models").exists():
            return path / "llama.cpp/models"
        for child in [d for d in path.iterdir() if d.is_dir()]:
            found = search_downwards(child, depth + 1)
            if found:
                return found
        return None

    # Search upwards
    found_path = search_upwards(start_path, 4)
    if found_path:
        return found_path  # Return the found 'llama.cpp/models' directory

    # Search downwards
    return search_downwards(start_path, 3)

# find the 'llama.cpp' directory
@st.cache_data
def find_llama_cpp_dir():
    # Search for llama.cpp directory two levels up
    current_dir = Path(__file__).resolve().parent
    for _ in range(2):
        current_dir = current_dir.parent
        llama_cpp_dir = current_dir / 'llama.cpp'
        if llama_cpp_dir.is_dir():
            return llama_cpp_dir

    # If not found, search two levels down
    current_dir = Path(__file__).resolve().parent
    for _ in range(2):
        current_dir = current_dir / 'llama.cpp'
        if current_dir.is_dir():
            return current_dir

    return None