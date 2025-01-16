import pytest

import telegram.features
from bot_mock import BotComponentMock
from components import Components

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_ping_feature():
    components = Components({'telegram-bot': {}, 'ping-feature': {}})
    components.append(telegram.features.PingFeatureComponent).append(BotComponentMock).start()

    bot_mock = components.find(BotComponentMock).get()

    class Empty:
        pass

    message = Empty()
    message.chat = Empty()
    message.chat.type = 'private'
    message.text = 'ping'
    assert await bot_mock.test_message(message) == ['Ping']

    message.chat.type = 'private'
    message.text = 'pong'
    assert await bot_mock.test_message(message) == []

    message.chat.type = 'group'
    message.text = 'ping'
    assert await bot_mock.test_message(message) == []
