import ast
import re
from enum import Enum

from telebot.util import quick_markup


def _pardon_markup(text, message):
    callback_data = {
        'type': 'banning-pardon',
        'user_id': message.from_user.id,
    }
    return quick_markup(
        {
            text: {
                'callback_data': str(callback_data)
            },
        },
        row_width=1,
    )

def _escape_markdown(text) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


class UserVerification(Enum):
    verified = 'verified'
    banned = 'banned'


class Users:
    verifying_users = dict()
    verified_users = set()
    banned_users = set()

    def __init__(self, users_storage, messages_storage):
        self._users_storage = users_storage
        self._messages_storage = messages_storage
        for user in users_storage.read_users_by_verification(
            UserVerification.verified.value
        ):
            self.verified_users.add(int(user[0]))
        for user in users_storage.read_users_by_verification(
            UserVerification.banned.value
        ):
            self.banned_users.add(int(user[0]))

    def get_username(self, user_id: int):
        user = self._users_storage.get_user(user_id)
        if user is None:
            return None
        return ('@' + user[2]) if user[2] is not None else user[1]

    def is_verified(self, user):
        return user.id in self.verified_users

    def is_banned(self, user):
        return user.id in self.banned_users

    def verify(self, user):
        verifications = self.verifying_users.get(user.id, 0) + 1
        self.verifying_users[user.id] = verifications
        if verifications < 3:
            return
        self._users_storage.add_user(
            user.id,
            user.first_name,
            user.username,
            UserVerification.verified.value)
        self.verifying_users.pop(user.id, None)
        self.verified_users.add(user.id)
        
    def ban(self, for_message):
        self._users_storage.add_user(
            for_message.from_user.id,
            for_message.from_user.first_name,
            for_message.from_user.username,
            UserVerification.banned.value)
        self._users_storage.update_ban_message(
            for_message.from_user.id,
            for_message.message_id,
            for_message.chat.id)
        self._messages_storage.write_message(
            for_message.message_id,
            for_message.chat.id,
            for_message.text)

        self.verifying_users.pop(for_message.from_user.id, None)
        self.banned_users.add(for_message.from_user.id)

    def pardon(self, user_id: int):
        self._users_storage.update_verification(user_id, UserVerification.verified.value)
        self.verifying_users.pop(user_id, None)
        self.banned_users.discard(user_id)
        self.verified_users.add(user_id)
        

class BanningFeature:
    def __init__(self, users_storage, messages_storage, bot, lang_model):
        self.users = Users(users_storage, messages_storage)
        self.messages_storage = messages_storage
        self.bot = bot
        self.lang_model = lang_model


    def check_message(self, message):
        return not self.users.is_verified(message.from_user)


    async def process_message(self, message):
        if not (self.users.is_banned(message.from_user) or 
            await self.lang_model.is_fishing(message.text)
        ):
            self.users.verify(message.from_user)
            if self.users.is_verified(message.from_user):
                congratulations = await self.lang_model.prompt(
                    f'Твой друг {message.from_user.first_name} победил в игру ' \
                     '"Рулетка Виталиков", которая проводится среди виталиков.' \
                     'Поздравь друга с победой и пообещай, что не будешь ' \
                     'его банить. Используй имя в его уменшительно-ласкательной ' \
                     'форме на русском языке.'
                )
                await self.bot.reply_to(message, congratulations)
            return
        
        if not self.users.is_banned(message.from_user):
            self.users.ban(message)

        if message.chat.type == 'private':
            await self.bot.reply_to(message, 'Я бы за такое забанил, но не буду')
            return

        if not await self._lamar_is_admin(message.chat.id):
            await self._ask_for_ban_with_callback(message)
            return

        await self._ban_with_callback(message)


    def check_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        return callback_data['type'] in ('banning-pardon')

        
    async def process_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        if callback_data['type'] == 'banning-pardon':
            username = self.users.get_username(int(callback_data['user_id']))

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

            if callback.message.reply_to_message is not None:
                username = callback.message.reply_to_message.from_user.first_name
            await self._pardon(callback_data['user_id'], username, callback.message.chat)


    async def _ban_with_callback(self, for_message):
        try:
            await self.bot.ban_chat_member(for_message.chat.id, for_message.from_user.id)
        except:
            await self._ask_for_ban_with_callback(for_message)
            return

        await self.bot.delete_message(for_message.chat.id, for_message.message_id)
        markup = _pardon_markup('Ты что ты что, а ну разбань', for_message)
        username = (('@' + for_message.from_user.username) 
                         if for_message.from_user.username is not None 
                         else for_message.from_user.first_name)
        notification = await self.lang_model.prompt(
            f'Ты забанил {username} за спам. Кратко опиши ' \
            f'случившееся. Расскажи об этом так, будто ты строгий полицейский ' \
            f'и арестовал преступника.')

        notification = _escape_markdown(notification)
        escaped_message = _escape_markdown(for_message.text)
        notification += f'\n\nСообщение: ||{escaped_message}||'
        
      
        await self.bot.send_message(
            for_message.chat.id,
            notification,
            parse_mode='MarkdownV2',
            reply_markup=markup)


    async def _ask_for_ban_with_callback(self, for_message):
        markup = _pardon_markup('Ты что ты что, это не спам', for_message)
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
        me = await self.bot.get_me()
        return any(member.user.id == me.id for member in admins)

