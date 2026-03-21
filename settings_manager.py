import json
import os

FILE = "settings.json"


def load_settings():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return {}


def save_settings(data):
    with open(FILE, "w") as f:
        json.dump(data, f)