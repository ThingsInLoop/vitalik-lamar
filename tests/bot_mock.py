import functools

from telebot.types import User


class BotComponentMock:
    name = 'telegram-bot'

    @staticmethod
    def create(components, settings):
        self = BotComponentMock()
        self.bot = BotMock()
        return self

    def get(self):
        return self.bot


class BotMock:
    def __init__(self):
        self.message_filters = []
        self.chat_member_filters = []
        self.replies = []
        self.unbans = []
        self.chats_admins = {}
        self.chats_admins_requests = 0

        self.user = User(id=1234, is_bot=True, first_name='VITALIK', last_name='LAMAR')

    def message_handler(self, func=lambda: True):
        def wrapper(action):
            self.message_filters.append((func, action))
            @functools.wraps(action)
            async def wrapped_f(*args, **kwargs):
                return await action(*args, **kwargs)
            return wrapped_f
        return wrapper

    def chat_member_handler(self, func=lambda: True):
        def wrapper(action):
            self.chat_member_filters.append((func, action))
            @functools.wraps(action)
            async def wrapped_f(*args, **kwargs):
                return await action(*args, **kwargs)
            return wrapped_f
        return wrapper

    async def get_chat_administrators(self, chat_id):
        self.chats_admins_requests += 1
        class Empty:
            pass
        member = Empty()
        member.user = self.user
        return self.chats_admins.get(chat_id, {member})

    async def reply_to(self, message, text):
        self.replies.append(text)

    async def unban_chat_member(self, chat_id, user_id, only_if_banned):
        self.unbans.append((chat_id, user_id, only_if_banned))

    async def test_message(self, message):
        self.replies.clear()
        for filter, action in self.message_filters:
            if filter(message):
                await action(message)
        return self.replies

    async def test_chat_member(self, update):
        self.replies.clear()
        for filter, action in self.chat_member_filters:
            if filter(update):
                await action(update)
        return self.replies
