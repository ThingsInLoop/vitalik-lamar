from telebot.async_telebot import AsyncTeleBot

from telegram.banning_feature import BanningFeature


class Bot:
    def __init__(
            self,
            config_component,
            lang_model,
            messages_storage,
            users_storage,
        ):
        self.config_component = config_component
        settings = config_component.get_config()["telegram-bot"]

        self.bot = AsyncTeleBot(settings["token"])
        self.lang_model = lang_model
        self.messages = messages_storage
        self.users = users_storage

        self.banning_feature = BanningFeature(
                                   self.users,
                                   self.messages,
                                   self.bot,
                                   self.lang_model)

        @self.bot.callback_query_handler(func=self.banning_feature.check_callback)
        async def check_for_fishing_callback(callback):
            await self.banning_feature.process_callback(callback)

        @self.bot.message_handler(func=self.banning_feature.check_message)
        async def check_for_fishing(message):
            await self.banning_feature.process_message(message)

    async def start(self):
        await self.bot.polling()

