#!/bin/bash
# this is the QCompanion bash installer for Linux 
# This installer is meant to be ran from a direct clone of the QCompanion repo and absolutely nowhere else.
# If you need to update, please reclone the repo and run the installer again and move your llama.cpp/models folder.

# These packages are needed to install or use ollama/companion.
COMMON_PACKAGES="make gcc git" 
VERSION="4"

# Function to install packages per distribution type.
install_packages() {
    if [[ "$1" == "Ubuntu" || "$1" == "Debian" ]]; then
        sudo apt update
        sudo apt install -y $COMMON_PACKAGES
    elif [[ "$1" == "Arch" ]]; then
        sudo pacman -Syu
        sudo pacman -S $COMMON_PACKAGES
    elif [[ "$1" == "RedHat" ]]; then
        sudo yum update
        sudo yum install -y $COMMON_PACKAGES
    fi
}

# Function to check Python 3.10 and python3.10-venv
check_python() {
    PYTHON_VERSION=$(python3 --version 2>/dev/null | grep -oP '(?<=Python )\d+\.\d+')
    PYTHON_VENV_PACKAGE="python3.10-venv" 

    if [[ $PYTHON_VERSION < 3.10 ]]; then
        echo "Python 3.10 or higher is not installed. Please install it using your distribution's package manager."
        case $1 in
            "Ubuntu"|"Debian")
                echo "Run: sudo apt install python3.10 python3.10-venv (or higher)" 
                ;;
            "Arch")
                echo "Run: sudo pacman -S python3.10 python3.10-venv (or higher)"  Adjust if package names differ
                ;;
            "RedHat")
                echo "Run: sudo yum install python3.10 python3.10-venv (or higher)" # Adjust if package names differ
                ;;
            *)
                echo "Unsupported distribution."
                ;;
        esac
    else
        echo "Python 3.10 or higher is installed."
    fi
}

# Function to create a Python virtual environment
create_python_venv() {
    if command -v python3.10 >/dev/null 2>&1; then
        python3.10 -m venv companion_venv
        echo "Virtual environment created with Python 3.10 in 'companion_venv' directory."
    elif command -v python3.11 >/dev/null 2>&1; then
        python3.11 -m venv companion_venv
        echo "Virtual environment created with Python 3.11 in 'companion_venv' directory."
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m venv companion_venv
        echo "Virtual environment created with default Python 3 in 'companion_venv' directory."
    else
        echo "No suitable Python 3 version found. Please install Python 3."
        return 1
    fi
}


# Function to activate the virtual environment
activate_venv() {
    source companion_venv/bin/activate
    echo "Virtual environment activated."
}

# Function to install dependencies from requirements.txt
pip_dependencies() {
    pip install -r requirements.txt
    echo "Dependencies installed from requirements.txt."
}

# Function to clone llama.cpp repository and run make in its directory
clone_and_make_llama_cpp() {
    git clone https://github.com/ggerganov/llama.cpp.git
    make -C llama.cpp
    echo "Cloned llama.cpp and ran make in the llama.cpp directory"
}

# END message when the installation is completed
END_MESSAGE="QCompanion successfully installed. Start with the start.sh script or by running streamlit serve Homepage.py in your terminal."

# TODO MAKE SURE YOU INCLUDE ALLLLLL THE DEPENDENCIES IN THE REQUIREMENTS.TXT FILE

main() {
    # Detect the OS
    OS="Unknown"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    fi
    echo "Starting Standard installation..."
    install_packages "$OS"
    check_python "$OS"
    clone_and_make_llama_cpp
    create_python_venv
    activate_venv
    pip_dependencies
    write_to_log "standard"
    echo "$END_MESSAGE" 
}

# Call the main function with all passed arguments
main "$@"
