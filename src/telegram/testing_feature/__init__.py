import json

import telegram
import language_model

class Component:
    name = 'testing-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.bot = components.find(telegram.BotComponent).get()

        self.llm = components.find(language_model.LanguageModelComponent).get()

        @self.bot.message_handler(func=lambda message: message.chat.type == 'private')
        async def ping_feature_message(message):
            print(json.dumps(message.json, indent=2, ensure_ascii=False))

        return self
