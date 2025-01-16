import telegram


class Component:
    name = 'ping-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.bot = components.find(telegram.BotComponent).get()

        @self.bot.message_handler(func=lambda message: message.chat.type == 'private' and
                                              message.text in ('ping', 'Ping'))
        async def ping_feature_message(message):
            await self.bot.reply_to(message, 'Ping')
        
        return self
