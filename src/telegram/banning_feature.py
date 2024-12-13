import ast

from telebot.util import quick_markup


class Users:
    verifying_users = dict()
    verified_users = set()
    banned_users = set()

    def __init__(self, users_storage, messages_storage):
        self._users_storage = users_storage
        self._messages_storage = messages_storage
        for user in users_storage.read_users_by_verification('verified'):
            self.verified_users.add(str(user[0]))
        for user in users_storage.read_users_by_verification('banned'):
            self.banned_users.add(str(user[0]))

    def is_verified(self, user):
        print('check is verified')
        print(self.verified_users)
        return str(user.id) in self.verified_users

    def is_banned(self, user):
        print('check is banned')
        return str(user.id) in self.banned_users

    def verify(self, user):
        print('verify')
        verifications = self.verifying_users.get(user.id, 0)
        self.verifying_users[user.id] = verifications + 1
        if verifications + 1 < 3:
            return
        self._users_storage.add_user(user.id, user.first_name, 'verified')
        self.verifying_users.pop(str(user.id), None)
        self.verified_users.add(user.id)
        
    def ban(self, for_message):
        print('ban')
        self._users_storage.add_user(
            for_message.from_user.id,
            for_message.from_user.first_name,
            'banned')
        self._users_storage.update_ban_message(
            for_message.from_user.id,
            for_message.message_id,
            for_message.chat.id)
        self._messages_storage.write_message(
            for_message.message_id,
            for_message.chat.id,
            for_message.text)

        self.verifying_users.pop(str(for_message.from_user.id), None)
        self.banned_users.add(str(for_message.from_user.id))
        print('done')

    def pardon(self, user_id):
        print('pardon')
        self._users_storage.update_verification(user_id, 'verified')
        try:
            self.banned_users.remove(str(user_id))
        finally:
            pass
        self.verified_users.add(str(user_id))
        

class BanningFeature:
    def __init__(self, users_storage, messages_storage, bot, lang_model):
        self.users = Users(users_storage, messages_storage)
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
                     'Кратко поздравь друга с победой и пообещай, что не будешь ' \
                     'его банить. Используй имя в его краткой форме ' \
                     'на русском языке.'
                )
                await self.bot.reply_to(message, congratulations)
            return
        
        self.users.ban(message)

        try:
            print('ban chat member')
            if not await self.bot.ban_chat_member(message.chat.id, message.from_user.id):
                print('ask for ban')
                await self._ask_for_ban_with_callback(message)
        finally:
            print('ask for ban')
            await self._ask_for_ban_with_callback(message)

        #await self.bot.delete_message(message.chat.id, message.message_id)

        #bot_message = await self.lang_model.prompt(f'Ты забанил {message.from_user.username} ')


    def check_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        return callback_data['type'] in ('banning-pardon')

        
    async def process_callback(self, callback):
        callback_data = ast.literal_eval(callback.data)
        if callback_data['type'] == 'banning-pardon':
            await self._remove_markup(callback.message)

            username = '(какой-то бот?)'
            if callback.message.reply_to_message is not None:
                username = callback.message.reply_to_message.from_user.first_name
            await self._pardon(callback_data['user_id'], username, callback.message.chat)


    async def _ask_for_ban_with_callback(self, for_message):
        callback_data = {
            'type': 'banning-pardon',
            'user_id': for_message.from_user.id,
        }
        markup = quick_markup(
            {
                'Ты что ты что, это не спам': {
                    'callback_data': str(callback_data)
                },
            },
            row_width=1,
        )
        username = for_message.from_user.username
        bot_message = await self.lang_model.prompt(f'Ты пытался забанить ' \
            f'@{username} за спам в чате, но по какой-то причине не ' \
            f'получилось. Возможно у тебя нет прав администратора. Кратко ' \
            f'попроси ребят из чата ' \
            f'забанить этого @{username}. Кратко извинись перед всеми за то,' \
            f'что у тебя не получилось забанить нарушителя')
        await self.bot.reply_to(for_message, bot_message, reply_markup=markup)


    async def _pardon(self, user_id, username, chat):
        self.users.pardon(user_id)
        
        apologizes = await self.lang_model.prompt(
            f'Ты перепутал, и обвинил друга {username} в отправке спама. ' \
            f'Кратко и с отмазкой извинись, скажи, что больше банить не будешь. ' \
            f'Используй имя в его уменьшительно-ласкательной форме на русском языке.')

        await self.bot.send_message(chat.id, apologizes)
        try:
            await self.bot.unban_chat_member(chat.id, user_id, only_if_banned=True)
        finally:
            pass

    async def _remove_markup(self, message):
        await self.bot.edit_message_reply_markup(
            message.chat.id, message.message_id, reply_markup=None
        )
