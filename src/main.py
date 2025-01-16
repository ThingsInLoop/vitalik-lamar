import asyncio
import argparse

from config import InitialConfig
from components import Components

import storage
import language_model
import telegram
import telegram.features


parser = argparse.ArgumentParser(
    prog="vitalik-lamar",
    description="Telegram bot for VITALIK RC group",
    epilog="Be humble",
)

parser.add_argument("-c", "--config-path")


async def main():
    args = parser.parse_args()

    initial_config = InitialConfig(args.config_path)
    components = Components(initial_config.get_config())

    (components
        .append(telegram.features.PingFeatureComponent)
        .append(telegram.features.BanningFeatureComponent)
        .append(telegram.BotComponent)
        .append(language_model.LanguageModelComponent)
        .append(language_model.IamTokenComponent)
        .append(storage.StorageComponent)
        .append(storage.MessagesComponent)
        .append(storage.UsersComponent)
        .start())

    print('Start polling!')

    await components.find(telegram.BotComponent).get().polling()


if __name__ == "__main__":
    asyncio.run(main())
