import json
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def add_user_to_config(api_id, api_hash, phone, string_session):
    configs = load_config()
    new_config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "telepon": phone,
        "string_sesi": string_session
    }
    configs.append(new_config)
    save_config(configs)
    logger.info(f"New user {phone} added to config.")