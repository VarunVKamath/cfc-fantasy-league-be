import subprocess
import sys

def install_if_missing(package):
    try:
        __import__(package)  # Try importing the package
        print(f"✅ {package} is already installed.")
    except ImportError:
        print(f"⏳ Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Mapping package names to import names (some packages are imported differently than their pip names)
packages = {
    "dill": "dill",
    "requests": "requests",
    "beautifulsoup4": "bs4",  # `beautifulsoup4` is installed as `bs4`
    "pandas": "pandas",
    "ipython": "IPython",
    "rapidfuzz": "rapidfuzz",
    "xlsxwriter": "xlsxwriter",
    "oauth2client": "oauth2client",
    "gspread": "gspread",
    "openpyxl": "openpyxl"
}

for pip_name, import_name in packages.items():
    install_if_missing(import_name)

print("✅ All required packages are ready!")
