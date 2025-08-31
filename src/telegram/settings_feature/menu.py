class Menu:
    def __init__(self, bot):
        self.bot = bot

        @self.bot.message_handler(chat_types=['private'], commands=['chats'])    
        async def setup_menu_state(self, message):
            await self.bot.reply_to(message, 'Not implemented yet!')
