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
    prog='vitalik-lamar',
    description='Telegram bot for VITALIK RC group',
    epilog='Be humble',
)

parser.add_argument('-c', '--config-path')
parser.add_argument('--mode', nargs='?', default='polling')
parser.add_argument('--log-level', nargs='?', default='info')

def parse_log_level(log_level: str):
    match log_level:
        case 'debug':
            return logging.DEBUG
        case 'info':
            return logging.INFO
        case 'warn':
            return logging.WARN
        case 'error':
            return logging.ERROR
        case _:
            return logging.DEBUG

async def main():
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=parse_log_level(args.log_level),
                        datefmt='%Y-%m-%d %H:%M:%S')

    initial_config = InitialConfig(args.config_path)
    components = Components(initial_config.get_config())

    (components
        .append(telegram.VoiceToTextFeatureComponent)
        .append(speech.SpeechComponent)
        .append(telegram.PingFeatureComponent)
        .append(telegram.BanningFeatureComponent)
        .append(telegram.BotComponent)
        .append(telegram.settings_feature.Component)
        .append(language_model.LanguageModelComponent)
        .append(iam_token.Component)
        .append(storage.StorageComponent)
        .append(storage.MessagesComponent)
        .append(storage.UsersComponent)
        .start())

    if args.mode == 'polling':
        logging.info('Start polling!')
        await components.find(telegram.BotComponent).start()
    if args.mode == 'draw':
        components.draw()



if __name__ == '__main__':
    asyncio.run(main())
