import json
import os
import subprocess
import sys
import shutil

def read_settings(json_file):
    """Reads settings from a JSON file and applies defaults."""
    try:
        with open(json_file, 'r') as file:
            settings = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)
    
    # Apply defaults if keys are missing
    settings.setdefault("env_name", "Kamodo_env")
    settings.setdefault("packages", [
        "netCDF4", "cdflib", "astropy", "ipython", "jupyter", "h5py", "sgp4", "spacepy", "hapiclient"
    ])
    return settings


def create_mamba_env(env_name):
    """Creates a Conda environment using Mamba."""
    try:
        subprocess.check_call(["mamba", "create", "-n", env_name, "python=3.7", "-y"])
        print(f"Conda environment '{env_name}' created successfully.")
    except Exception as e:
        print(f"Error creating Conda environment: {e}")
        sys.exit(1)

def install_packages(env_name, packages):
    """Installs packages in the Conda environment using Mamba."""
    try:
        subprocess.check_call(["mamba", "install", "-n", env_name, "-c", "conda-forge"] + packages + ["-y"])
        print(f"Packages installed successfully in environment '{env_name}'.")

    except Exception as e:
        print(f"Error installing packages in environment '{env_name}': {e}")
        sys.exit(1)

def install_kamodo_ccmc(env_name):
    """Clones and installs the kamodo_ccmc package."""
    git_executable = shutil.which("git")
    if not git_executable:
        print("Git is not installed or not found in PATH. Please install Git and try again.")
        sys.exit(1)

    repo_url = "https://github.com/nasa/Kamodo.git"
    clone_dir = "Kamodo"

    try:
        if os.path.exists(clone_dir):
            print(f"Directory '{clone_dir}' already exists. Deleting it to proceed.")
            shutil.rmtree(clone_dir)
        
        print("Cloning the Kamodo repository...")
        subprocess.check_call([git_executable, "clone", repo_url, clone_dir])
        print("Repository cloned successfully.")

        # Install Kamodo
        print("Installing Kamodo...")
        subprocess.check_call([
            "conda", "run", "-n", env_name, "pip", "install", "Kamodo"
        ])
        print(f"Kamodo installed successfully in {env_name}.")
    except Exception as e:
        print(f"Error installing Kamodo: {e}")
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
        print(f"Jupyter kernel for environment '{env_name}' installed successfully.")
    except Exception as e:
        print(f"Error enabling Jupyter kernel: {e}")
        sys.exit(1)

def tear_down_env(env_name):
    """Deletes the Conda environment."""
    try:
        subprocess.check_call(["conda", "env", "remove", "-n", env_name, "-y"])
        print(f"Conda environment '{env_name}' has been removed.")
    except Exception as e:
        print(f"Error removing Conda environment '{env_name}': {e}")
        sys.exit(1)

def main():
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
