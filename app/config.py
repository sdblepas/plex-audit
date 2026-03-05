import yaml
import os

CONFIG_FILE = "/app/config.yml"


def load_config():

    if not os.path.exists(CONFIG_FILE):
        raise RuntimeError("config.yml not found")

    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()


def cfg(section, key=None):

    if key:
        return CONFIG.get(section, {}).get(key)

    return CONFIG.get(section)