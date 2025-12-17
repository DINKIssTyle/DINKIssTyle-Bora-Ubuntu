import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def get_hotkey():
        config = ConfigManager.load_config()
        return config.get('hotkey', 'ctrl+shift+s')

    @staticmethod
    def set_hotkey(hotkey_str):
        config = ConfigManager.load_config()
        config['hotkey'] = hotkey_str
        ConfigManager.save_config(config)
