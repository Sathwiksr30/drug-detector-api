import subprocess
import sys

# Uninstall opencv-python if present
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"], check=True)
# Install opencv-python-headless
subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python-headless==4.11.0.86"], check=True)
# Log installed packages for debugging
with open("installed_packages.txt", "w") as f:
    subprocess.run([sys.executable, "-m", "pip", "list"], stdout=f, text=True)