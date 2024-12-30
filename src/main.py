import asyncio
import argparse


from config import InitialConfig
from components import Components


from telegram.bot import Bot
from language_model.yandexgpt import Model

import storage


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
        .append(storage.StorageComponent)
        .append(storage.MessagesComponent)
        .append(storage.UsersComponent)
        .start())


if __name__ == "__main__":
    asyncio.run(main())
