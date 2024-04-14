import streamlit as st

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