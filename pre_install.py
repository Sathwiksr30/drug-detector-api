import subprocess
import sys

# Uninstall opencv-python if present
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"])