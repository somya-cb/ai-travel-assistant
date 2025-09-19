# src/services/config.py
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"

def load_config(path=None):
    """Load configuration from JSON file."""
    path = Path(path) if path else CONFIG_PATH
    with open(path, "r") as f:
        return json.load(f)
