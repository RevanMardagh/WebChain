# utils/config.py
import json
import os
from utils import colorize, Colors

CONFIG_PATH = os.path.expanduser("~/.recon_config.json")

DEFAULT_CONFIG = {
    "gemini_api_key": ""
}

def load_config(require_ai: bool = False) -> dict:
    """
    Load the config file.
    If require_ai=True, will prompt user for Gemini API key if missing.
    If require_ai=False, returns existing config or default without prompting.
    """
    if not os.path.exists(CONFIG_PATH):
        if require_ai:
            save_config(DEFAULT_CONFIG)
            return first_time_setup()
        else:
            return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print(colorize("[ERROR] Config file is corrupted. Rebuilding it.", Colors.ERROR))
        save_config(DEFAULT_CONFIG)
        if require_ai:
            return first_time_setup()
        else:
            return DEFAULT_CONFIG.copy()

    # If AI required and key is empty, prompt
    if require_ai and not config.get("gemini_api_key"):
        return first_time_setup()

    return config


def save_config(config: dict):
    """Save config file with secure permissions."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass


def first_time_setup() -> dict:
    """Prompt for Gemini API key and save it."""
    print(colorize("\n=== AI Configuration Required ===", Colors.HEADER))
    print("To enable AI endpoint analysis, enter your Gemini API key.\n")
    key = input("Gemini API Key: ").strip()

    cfg = {"gemini_api_key": key}
    save_config(cfg)

    if key:
        print(colorize("[INFO] Gemini API key saved.", Colors.OK))
    else:
        print(colorize("[WARN] No API key provided. AI will not run.", Colors.WARN))

    return cfg
