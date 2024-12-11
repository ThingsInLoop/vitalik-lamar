import yaml
import asyncio


class ConfigComponent:
    config_path: str
    config: dict

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.read_config()
        self.periodic_update = asyncio.create_task(
            self.update_config(),
            name="update-config",
        )

    def read_config(self):
        with open(self.config_path) as config_yaml:
            return yaml.safe_load(config_yaml)

    async def update_config(self, period_sec=5):
        while True:
            await asyncio.sleep(period_sec)
            self.config = self.read_config()

    def get_config(self):
        return self.config
