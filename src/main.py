import asyncio
import argparse
import logging

from config import InitialConfig
from components import Components

import speech
import storage
import language_model
import telegram
import iam_token


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
        .append(telegram.VoiceToTextFeatureComponent)
        .append(speech.SpeechComponent)
        .append(telegram.PingFeatureComponent)
        .append(telegram.BanningFeatureComponent)
        .append(telegram.BotComponent)
        .append(language_model.LanguageModelComponent)
        .append(iam_token.Component)
        .append(storage.StorageComponent)
        .append(storage.MessagesComponent)
        .append(storage.UsersComponent)
        .start())

    logging.basicConfig(level=logging.INFO)
    logging.info('Start polling!')

    await components.find(telegram.BotComponent).get().polling()


if __name__ == "__main__":
    asyncio.run(main())
