import subprocess
import sys
import spacy
import os

# Ensure permissions
os.system("chmod -R 777 /home/adminuser/venv")
# Install SpaCy and model
subprocess.run([sys.executable, "-m", "pip", "install", "spacy==3.7.5"], check=True)
subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
# Verify installation
try:
    spacy.load("en_core_web_sm")
    with open("spacy_install_success.txt", "w") as f:
        f.write("en_core_web_sm installed successfully")
except Exception as e:
    with open("spacy_install_error.txt", "w") as f:
        f.write(str(e))