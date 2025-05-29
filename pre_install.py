import subprocess
import sys

# Uninstall opencv-python if present
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"])
# Install opencv-python-headless first
subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python-headless==4.11.0.86"])