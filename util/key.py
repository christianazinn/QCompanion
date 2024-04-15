# IMPORTS ---------------------------------------------------------------------------------
from cryptography.fernet import Fernet
from pathlib import Path

# FUNCTIONS ---------------------------------------------------------------------------------

# Function to load the existing key
def load_key():
    key_dir = Path('.') / '.key'
    key_file_path = key_dir / 'encryption.key'
    return key_file_path.read_bytes()

# Encrypt the token
def encrypt_token(token):
    key = load_key()
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode())
    return encrypted_token.decode()

# Decrypt the token
def decrypt_token(encrypted_token):
    key = load_key()
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()

# Generate a new key - to be called by the user
def generate_new_key():
    key_dir = Path('.') / '.key'
    key_file_path = key_dir / 'encryption.key'
    
    # Check if the key file exists and delete it
    if key_file_path.exists():
        try:
            key_file_path.unlink()  # Deletes the file
            print("Existing key file deleted.")
        except Exception as e:
            return f"Error deleting existing key: {e}"

    # Generate new key
    root_dir = Path(__file__).parent.parent
    try:
        key = Fernet.generate_key()
        if not key_dir.exists():
            key_dir.mkdir(parents=True, exist_ok=True)
        with open(key_file_path, 'wb') as key_file:
            key_file.write(key)
        return "New private key generated successfully."
    except e:
        return f"Error generating new key: {e}"