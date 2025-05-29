import subprocess
import sys

# Uninstall opencv-python
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"], check=True)
# Install opencv-python-headless
subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python-headless==4.11.0.86"], check=True)
# Install ultralytics and easyocr without dependencies
subprocess.run([sys.executable, "-m", "pip", "install", "ultralytics==8.2.90", "--no-deps"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "easyocr==1.7.2", "--no-deps"], check=True)
# Log installed packages
with open("installed_packages.txt", "w") as f:
    subprocess.run([sys.executable, "-m", "pip", "list"], stdout=f, text=True)