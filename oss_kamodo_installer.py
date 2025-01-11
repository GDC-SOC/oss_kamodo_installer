"""
OSS Kamodo Installer

This script automates the setup and management of a Conda environment 
for the Kamodo framework. It handles environment creation, package 
installation, Kamodo setup, and Jupyter kernel configuration.

Features:
- Reads configuration from `oss_kamodo_installer_settings.json`.
- Provides a `--clean` option to delete the environment.
- Logs actions and errors to a timestamped file in the `logs/` directory.

Usage:
- To set up the environment: `python oss_kamodo_installer.py`
- To remove the environment: `python oss_kamodo_installer.py --clean`
"""
import json
import os
import subprocess
import sys
import shutil
import logging
from datetime import datetime

# Configure Logging
# Ensure the 'logs/' directory exists
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Generate log filename with date and time
current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = os.path.join(LOG_DIR, f'oss_kamodo_installer_{current_time}.log')

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Default logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    filename=log_filename,  # File to store logs
    filemode='a'  # Append to the log file
)

# Add a console handler for real-time output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

# Log the initialization message as the first line in the log
INITIAL_MESSAGE = f"Log file created: {log_filename}"
logging.info(INITIAL_MESSAGE)

def read_settings(json_file):
    """Reads settings from a JSON file and applies defaults."""
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            settings = json.load(file)
    except FileNotFoundError:
        logging.error("JSON file not found: %s", json_file)
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON file: %s", json_file)
        sys.exit(1)
    except IOError as e:
        logging.error("I/O error while reading JSON file: %s", e)
        sys.exit(1)

    # Apply defaults if keys are missing
    settings.setdefault("env_name", "Kamodo_env")
    settings.setdefault("packages", [
        "netCDF4", "cdflib", "astropy", "ipython",
        "jupyter", "h5py", "sgp4", "spacepy", "hapiclient"
    ])
    return settings


def create_mamba_env(env_name):
    """Creates a Conda environment using Mamba."""
    try:
        logging.info("Creating Conda environment: %s", env_name)
        subprocess.check_call(["mamba", "create", "-n", env_name, "python=3.7", "-y"])
        logging.info("Conda environment %s created successfully.", env_name)
    except subprocess.CalledProcessError as e:
        logging.error(
            "Mamba command failed with exit code %s while creating Conda environment %s.",
            e.returncode, env_name)
        sys.exit(1)
    except FileNotFoundError:
        logging.error(
            "Mamba is not installed or not found in PATH. Please install Mamba and try again."
        )
        sys.exit(1)
    except OSError as e:
        logging.error("An OS error occurred while creating Conda environment %s: %s", env_name, e)
        sys.exit(1)

def install_packages(env_name, packages):
    """Installs packages in the Conda environment using Mamba."""
    try:
        subprocess.check_call(["mamba",
                               "install",
                               "-n",
                               env_name,
                               "-c",
                               "conda-forge"] + packages + ["-y"])
        logging.info("Packages installed successfully in environment %s.", env_name)
    except subprocess.CalledProcessError as e:
        logging.error(
            "Mamba command failed with exit code %s while installing packages in environment %s.",
            e.returncode, env_name)
        sys.exit(1)
    except FileNotFoundError:
        logging.error(
            "Mamba is not installed or not found in PATH. Please install Mamba and try again."
        )
        sys.exit(1)
    except OSError as e:
        logging.error(
            "An OS error occurred while installing packages in environment %s: %s",
                      env_name, e)
        sys.exit(1)

def install_kamodo_ccmc(env_name):
    """Clones and installs the kamodo_ccmc package."""
    git_executable = shutil.which("git")
    if not git_executable:
        logging.error(
            "Git is not installed or not found in PATH. Please install Git and try again."
        )
        sys.exit(1)

    repo_url = "https://github.com/nasa/Kamodo.git"
    clone_dir = "Kamodo"

    try:
        if os.path.exists(clone_dir):
            logging.info("Directory %s already exists. Deleting it to proceed.", clone_dir)
            shutil.rmtree(clone_dir)

        logging.info("Cloning the Kamodo repository...")
        subprocess.check_call([git_executable, "clone", repo_url, clone_dir])
        logging.info("Repository cloned successfully.")

        # Install Kamodo
        logging.info("Installing Kamodo...")
        subprocess.check_call([
            "conda", "run", "-n", env_name, "pip", "install", "Kamodo"
        ])
        logging.info("Kamodo installed successfully in %s.", env_name)
    except subprocess.CalledProcessError as e:
        logging.error("Command failed with exit code %s: %s", e.returncode, e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error("Required executable not found: %s", e)
        sys.exit(1)
    except PermissionError as e:
        logging.error("Permission error occurred: %s", e)
        sys.exit(1)
    except OSError as e:
        logging.error("An OS error occurred: %s", e)
        sys.exit(1)

def enable_jupyter_kernel(env_name):
    """Adds the Conda environment as a Jupyter kernel."""
    try:
        subprocess.check_call(["mamba", "install", "-n", env_name, "ipykernel", "-y"])
        subprocess.check_call([
            "conda", "run", "-n", env_name,
            "python", "-m", "ipykernel", "install",
            "--user", "--name", env_name,
            "--display-name", f"Python ({env_name})"
        ])
        logging.info("Jupyter kernel for environment %s installed successfully.",
                     env_name)
    except subprocess.CalledProcessError as e:
        logging.error(
            "Command failed with exit code %s while enabling Jupyter kernel for environment %s.",
            e.returncode, env_name)
        sys.exit(1)
    except FileNotFoundError:
        logging.error(
            "Required executable not found. Ensure that Mamba, Conda, and Python are in PATH."
        )
        sys.exit(1)
    except PermissionError as e:
        logging.error(
            "Permission error while enabling Jupyter kernel: %s",
            e)
        sys.exit(1)
    except OSError as e:
        logging.error(
            "An OS error occurred while enabling Jupyter kernel: %s",
            e)
        sys.exit(1)

def tear_down_env(env_name):
    """Deletes the Conda environment."""
    try:
        subprocess.check_call(["conda", "env", "remove", "-n", env_name, "-y"])
        logging.info("Conda environment '%s' has been removed.", env_name)
    except subprocess.CalledProcessError as e:
        logging.error("Failed to remove Conda environment '%s'. Process error: %s", env_name, e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(
            "The 'conda' command was not found. Ensure Conda is installed and in PATH. Error: %s",
            e)
        sys.exit(1)

def main():
    """
    Main function for setting up or cleaning up a Conda environment for the Kamodo installer.

    This function reads user settings from a JSON file, creates a Conda environment using Mamba,
    installs required packages, installs Kamodo, and enables the Jupyter kernel for the environment.
    It also provides an option to clean up (tear down) the environment if specified via a 
    command-line argument.

    Workflow:
    1. Reads settings from a JSON file (`oss_kamodo_installer_settings.json`).
    2. Checks for the `--clean` flag in command-line arguments to tear down the environment.
    3. Creates the Conda environment if the `--clean` flag is not set.
    4. Installs required packages in the environment.
    5. Installs Kamodo from its repository.
    6. Enables the Jupyter kernel for the environment.

    Command-line Arguments:
        --clean : Optional argument to remove the specified Conda environment.

    Note:
        Ensure that the required utilities (`mamba`, `conda`, `Kamodo`) are available
        in the system's PATH.

    """
    settings_file = "oss_kamodo_installer_settings.json"  # JSON file containing user settings
    settings = read_settings(settings_file)

    env_name = settings["env_name"]
    packages = settings["packages"]

    # Option to tear down the environment
    if "--clean" in sys.argv:
        tear_down_env(env_name)
        return

    # Step 1: Create the Conda environment using Mamba
    create_mamba_env(env_name)

    # Step 2: Install required packages
    install_packages(env_name, packages)

    # Step 3: Clone and install Kamodo
    install_kamodo_ccmc(env_name)

    # Step 4: Enable the Jupyter kernel for the environment
    enable_jupyter_kernel(env_name)

if __name__ == "__main__":
    main()
