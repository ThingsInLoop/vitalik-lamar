import pytest
import asyncio

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
    components.find(telegram.JoinLimiterComponent).stop()


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
    components.find(telegram.JoinLimiterComponent).stop()

    
@pytest.mark.asyncio
async def test_join_limiter_component_multiple_removals():
    components = Components({'telegram-bot': {},
                            'join-limiter-feature': {
                                'chats-default-rate': {
                                    'capacity': 1,
                                    'window': '00:10.0'
                                }
                            }})
    components.append(telegram.JoinLimiterComponent).append(BotComponentMock).start()

    bot_mock = components.find(BotComponentMock).get()

    async def join_request(user_id, bot):
        update = make_update()
        await asyncio.sleep(0.01)
        update.from_user.id = i

        await bot_mock.test_chat_member(update)
    
    tasks = []
    for i in range(100):
        tasks.append(asyncio.create_task(join_request(i, bot_mock)))
    for task in tasks:
        await task
    assert len(bot_mock.unbans) == 99

    components.find(telegram.JoinLimiterComponent).stop()

    
