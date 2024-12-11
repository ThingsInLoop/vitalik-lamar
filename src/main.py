import asyncio
import argparse

from telegram.bot import Bot
from language_model.yandexgpt import Model
from storage.messages import Messages
from config.component import ConfigComponent


parser = argparse.ArgumentParser(
    prog="vitalik-lamar",
    description="Telegram bot for VITALIK RC group",
    epilog="Be humble",
)

parser.add_argument("-c", "--config-path")


async def main():
    args = parser.parse_args()

    config_component = ConfigComponent(args.config_path)
    model = Model(config_component)
    messages_storage = Messages(config_component)
    bot = Bot(config_component, model, messages_storage)

    model_task = asyncio.create_task(model.start(), name="language-model")
    bot_task = asyncio.create_task(bot.start(), name="telegram-bot")
    await asyncio.gather(*[model_task, bot_task])


if __name__ == "__main__":
    asyncio.run(main())
