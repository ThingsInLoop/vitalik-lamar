import yaml


class InitialConfig:
    config_path: str
    config: dict

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.read_config()

    def read_config(self):
        with open(self.config_path, mode='r', encoding='utf-8') as config_yaml:
            return yaml.safe_load(config_yaml)

    def get_config(self):
        return self.config
