import functools


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
    message_filters = []
    replies = []

    def message_handler(self, func=lambda: True):
        def wrapper(action):
            self.message_filters.append((func, action))
            @functools.wraps(action)
            async def wrapped_f(*args, **kwargs):
                return await action(*args, **kwargs)
            return wrapped_f
        return wrapper

    async def reply_to(self, message, text):
        self.replies.append(text)

    async def test_message(self, message):
        self.replies.clear()
        for filter, action in self.message_filters:
            if filter(message):
                await action(message)
        return self.replies
