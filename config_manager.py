
import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file="db_config.json"):
        self.config_file = config_file
        self.config_path = Path(config_file)
    
    def save_config(self, config_data):
        """Save database configuration to local file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_config(self):
        """Load database configuration from local file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    
    def clear_config(self):
        """Remove saved configuration"""
        try:
            if self.config_path.exists():
                self.config_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing config: {e}")
            return False
    
    def config_exists(self):
        """Check if configuration file exists"""
        return self.config_path.exists()
