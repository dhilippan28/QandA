# run.py
import os
from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quora_clone.settings")
    CommandLineInterface().run(["-b", "0.0.0.0", "-p", "8000", "quora_clone.asgi:application"])
