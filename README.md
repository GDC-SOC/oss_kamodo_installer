
# OSS Kamodo Installer

The `oss_kamodo_installer` script automates the setup and installation of the Kamodo package in a Conda environment. It ensures that all dependencies are installed and configured properly for a seamless experience.

---

## Features

- Creates a Conda environment using Mamba for faster dependency resolution.
- Installs all required dependencies for Kamodo.
- Clones the Kamodo repository from GitHub and installs it.
- Configures the environment as a Jupyter kernel for interactive use.
- Includes a cleanup option to remove the environment and associated files.

---

## How to Run

### 1. Clone the Repository
Clone the `oss_kamodo_installer` repository to your local machine:
```bash
git clone https://github.com/<your-username>/oss_kamodo_installer.git
cd oss_kamodo_installer
```

### 2. Prepare the Settings
Edit the `settings.json` file to configure the environment name and required packages (optional). Default settings are as follows:
```json
{
    "env_name": "Kamodo_env",
    "packages": [
        "netCDF4", "cdflib", "astropy", "ipython", "jupyter", "h5py", "sgp4", "spacepy", "hapiclient"
    ]
}
```

### 3. Run the Script
Execute the script using Python:
```bash
python oss_kamodo_installer.py
```