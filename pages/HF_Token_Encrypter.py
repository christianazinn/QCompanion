# FILESTATUS: unknown, needs testing. Last updated v0.1.0
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
from st_pages import add_indentation
from util.key import encrypt_token, generate_new_key

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

# def show_token_encrypt_page():
st.title("Token Encryption")

token = st.text_input("Enter your Hugging Face Token", type="password")

if st.button("Encrypt Token"):
    if token:
        encrypted_token = encrypt_token(token)
        st.text_area("Encrypted Token", encrypted_token, height=100)
    else:
        st.error("Please enter a token to encrypt.")

if st.button("Generate New Private Key"):
    message = generate_new_key()
    st.text(message)

# Uncomment this line to run this script directly for testing
# show_token_encrypt_page()
with st.expander("Token Encryption Guide", expanded=False):
    st.markdown("""
    **Token Encryption Guide**

    This page assists you in encrypting your Hugging Face token for enhanced security.

    **Why Encrypt Your Token?**
    
    Encrypting your Hugging Face token adds an extra layer of security, protecting it from unauthorized access. It is particularly useful when you deploy scripts in shared environments.

    **How to Encrypt Your Token:**

    1. **Enter Your Token:** Type your Hugging Face token into the input field.
    2. **Encrypt:** Click the 'Encrypt Token' button to encrypt your token.
    3. **Use Your Encrypted Token:** The encrypted token will be displayed. You can now use this encrypted token within this app for secure uploading to Hugging Face.
    4. **Secure Usage:** Store your encrypted token securely. It will be your secure key for uploads in this application.

    Encrypting your token ensures its security and enables you to upload to Hugging Face safely within this app.
    """)
