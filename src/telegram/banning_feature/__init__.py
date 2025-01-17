import ast
from enum import Enum

from telebot.formatting import escape_markdown

import storage
import language_model
import telegram
import telegram.banning_feature.utils as utils
from telegram.banning_feature.users import Users


class Component:
    name = 'banning-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        storage_component = components.find(storage.StorageComponent)
        llm = components.find(language_model.LanguageModelComponent).get()
        bot = components.find(telegram.BotComponent).get()

        self.banning_feature = BanningFeature(storage_component.get_users(),
                                              storage_component.get_messages(),
                                              bot,
                                              llm)

        @bot.callback_query_handler(func=self.banning_feature.check_callback)
        async def banning_feature_callback(callback):
            await self.banning_feature.process_callback(callback)

        @bot.message_handler(func=self.banning_feature.check_message)
        async def banning_feature_message(message):
            await self.banning_feature.process_message(message)

        return self
        

class BanReason(Enum):
    fishing = 'спам'
    too_many_custom_emojis = 'эмодзи спам'
    already_banned = 'когда-то уже банил'
        

class BanningFeature:
    def __init__(self, users_storage, messages_storage, bot, lang_model):
        self.users = Users(users_storage, messages_storage)
        self.messages_storage = messages_storage
        self.bot = bot
        self.lang_model = lang_model


    def check_message(self, message):
        return not self.users.is_verified(message.from_user)


    async def process_message(self, message):
        ban_reason = await self._get_ban_reason(message)
        if ban_reason is None:
            self.users.verify(message.from_user)
            return
        
        if message.chat.type == 'private':
            await self.bot.reply_to(message, f'{ban_reason.value}')
            return

        if not self.users.is_banned(message.from_user):
            self.users.ban(message)

        if not await self._lamar_is_admin(message.chat.id):
            await self._ask_for_ban_with_callback(message)
            return

        await self._ban_with_callback(message, ban_reason)


    def check_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        return callback_data['type'] in ('banning-pardon')

        
    async def process_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        if callback_data['type'] == 'banning-pardon':
            username = self.users.get_username(int(callback_data['user_id']))
            if callback.message.reply_to_message is not None:
                username = callback.message.reply_to_message.from_user.first_name

            admins = await self.bot.get_chat_administrators(callback.message.chat.id)
            if not any(member.user.id == callback.from_user.id for member in admins):
                ask_for_admins = await self.lang_model.prompt(
                    f'Друг {callback.from_user.first_name} пытался разбанить ' \
                    f'пользователя {username}, но {callback.from_user.first_name} ' \
                    f'не является администратором чата. Попроси друга обратиться к ' \
                    f'администраторам, чтобы они разбанили за него. Обращайся по имени ' \
                    f'в краткой форме на русском языке.')
                await self.bot.reply_to(callback.message, ask_for_admins)
                return

            await self._remove_markup(callback.message)
            await self._pardon(callback_data['user_id'], username, callback.message.chat)


    async def _get_ban_reason(self, message):
        if self.users.is_banned(message.from_user):
            return BanReason.already_banned
        if  utils.too_many_custom_emojis(message):
            return BanReason.too_many_custom_emojis
        if await self.lang_model.is_fishing(message.text):
            return BanReason.fishing
        return None



    async def _ban_with_callback(self, for_message, reason):
        try:
            await self.bot.ban_chat_member(for_message.chat.id, for_message.from_user.id)
        except Exception:
            await self._ask_for_ban_with_callback(for_message)
            return

        await self.bot.delete_message(for_message.chat.id, for_message.message_id)
        markup = utils.pardon_markup('Ты что ты что, а ну разбань', for_message)
        username = (('@' + for_message.from_user.username) 
                         if for_message.from_user.username is not None 
                         else for_message.from_user.first_name)
        notification = escape_markdown(f'Забанил {username}. Повод: {reason.value}')
        escaped_message = escape_markdown(for_message.text)
        notification += f'\n\nСообщение: ||{escaped_message}||'
        
      
        await self.bot.send_message(
            for_message.chat.id,
            notification,
            parse_mode='MarkdownV2',
            reply_markup=markup)


    async def _ask_for_ban_with_callback(self, for_message):
        markup = utils.pardon_markup('Ты что ты что, это не спам', for_message)
        username = (('@' + for_message.from_user.username) 
                         if for_message.from_user.username is not None 
                         else for_message.from_user.first_name)
        bot_message = await self.lang_model.prompt(f'Ты пытался забанить ' \
            f'{username} за спам в чате, но по какой-то причине не ' \
            f'получилось. Возможно у тебя нет прав администратора. Кратко ' \
            f'попроси ребят из чата ' \
            f'забанить этого @{username}. Кратко извинись перед всеми за то,' \
            f'что у тебя не получилось забанить нарушителя')
        await self.bot.reply_to(for_message, bot_message, reply_markup=markup)


    async def _pardon(self, user_id, username, chat):
        self.users.pardon(user_id)

        prompt = f'Ты перепутал, и обвинил друга по имени {username} в отправке спама. ' \
            f'Кратко извинись, скажи, что больше банить не будешь. ' \
            f'Используй имя в его уменьшительно-ласкательной форме на русском языке.'

        member = await self.bot.get_chat_member(chat.id, user_id)
        if member.status == 'kicked':
            prompt = f'Ты случайно выгнал из чата друга по имени {username}. ' \
                     f'Попроси ребят из чата добавить его обратно, извинись и ' \
                     f'пообещай, что больше не будешь его банить.'
        
        apologizes = await self.lang_model.prompt(prompt)

        await self.bot.send_message(chat.id, apologizes)
        if await self._lamar_is_admin(chat.id):
            await self.bot.unban_chat_member(chat.id, user_id, only_if_banned=True)

    async def _remove_markup(self, message):
        await self.bot.edit_message_reply_markup(
            message.chat.id, message.message_id, reply_markup=None
        )

    async def _lamar_is_admin(self, chat_id: int):
        admins = await self.bot.get_chat_administrators(chat_id)
        return any(member.user.id == self.bot.user.id for member in admins)

