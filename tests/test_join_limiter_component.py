import pytest

import telegram
from bot_mock import BotComponentMock
from components import Components

pytest_plugins = ('pytest_asyncio',)

def make_update():
    class Empty:
        pass

    update = Empty()
    update.chat = Empty()
    update.chat.id = 1
    update.from_user = Empty()
    update.from_user.id = 1
    update.old_chat_member = Empty()
    update.old_chat_member.status = 'left'
    update.new_chat_member = Empty()
    update.new_chat_member.status = 'member'

    return update

@pytest.mark.asyncio
async def test_join_limiter_component():
    components = Components({'telegram-bot': {},
                            'join-limiter-feature': {
                                'chats-default-rate': {
                                    'capacity': 2,
                                    'window': '00:00.1'
                                }
                            }})
    components.append(telegram.JoinLimiterComponent).append(BotComponentMock).start()

    bot_mock = components.find(BotComponentMock).get()
    update = make_update()

    await bot_mock.test_chat_member(update)
    assert len(bot_mock.unbans) == 0
    assert bot_mock.chats_admins_requests == 0
    await bot_mock.test_chat_member(update)
    assert len(bot_mock.unbans) == 0
    assert bot_mock.chats_admins_requests == 0
    await bot_mock.test_chat_member(update)
    assert len(bot_mock.unbans) == 1
    assert bot_mock.chats_admins_requests == 1
    assert bot_mock.unbans[0] == (1, 1, False)


@pytest.mark.asyncio
async def test_join_limiter_component_zero_capacity():
    components = Components({'telegram-bot': {},
                            'join-limiter-feature': {
                                'chats-default-rate': {
                                    'capacity': 0,
                                    'window': '00:00.1'
                                }
                            }})
    components.append(telegram.JoinLimiterComponent).append(BotComponentMock).start()

    bot_mock = components.find(BotComponentMock).get()
    update = make_update()

    await bot_mock.test_chat_member(update)
    assert len(bot_mock.unbans) == 1
    assert bot_mock.unbans[0] == (1, 1, False)
    
