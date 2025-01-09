from telebot.async_telebot import AsyncTeleBot
from collections.abc import Callable


class Component:
    name = 'telegram-bot'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.bot = AsyncTeleBot(settings['token'])
        return self

    def get(self):
        return self.bot

