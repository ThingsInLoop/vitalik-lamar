import logging

from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, BotCommandScopeAllPrivateChats


class Component:
    name = 'telegram-bot'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.bot = AsyncTeleBot(settings['token'])
        self.private_commands = list()
        return self

    def add_command_for_private_chats(self, command: str, description: str = 'None'):
        self.private_commands.append(BotCommand(command, description))

    async def start(self):
        try:
            if len(self.private_commands) > 0:
                await self.bot.set_my_commands(self.private_commands,
                                                BotCommandScopeAllPrivateChats())
            await self.bot.polling(non_stop=True, interval=0.5)
        except Exception as e:
            logging.error(f'Exception on telegram bot startup: {e}')
            raise e

    def get(self):
        return self.bot

