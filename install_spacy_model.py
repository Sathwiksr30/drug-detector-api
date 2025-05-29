import spacy
import subprocess
import sys

try:
    spacy.load("en_core_web_sm")
except:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])