import datetime
import logging

import telegram
import utils

class JoinLimiterComponent:
    name = 'join-limiter-feature'

    @staticmethod
    def create(components, settings):
        self = JoinLimiterComponent()

        self.chats_limiters = {}
        self.chats_default_capacity = settings['chats-default-rate']['capacity']
        time_obj = datetime.datetime.strptime(settings['chats-default-rate']['window'], '%M:%S.%f')
        self.chats_default_window = datetime.timedelta(
            hours=time_obj.hour,
            minutes=time_obj.minute,
            seconds=time_obj.second,
            microseconds=time_obj.microsecond
        )
        self.bot = components.find(telegram.BotComponent).get()

        @self.bot.chat_member_handler(func=lambda update: update.old_chat_member.status == 'left' and
                                                          update.new_chat_member.status == 'member')
        async def new_chat_member_handler(update):
            await self.process_new_chat_member(update)

        # TODO получение сообщений о вступлениях в чат. Чтобы было что удалять
        # @self.bot.message_handler(content_types=['new_chat_members'])

        return self

    async def process_new_chat_member(self, update):
        limiter = self.chats_limiters.setdefault(
            update.chat.id,
            utils.SlidingWindowRateLimiter(
                self.chats_default_capacity,
                self.chats_default_window
            )
        )

        if limiter.acquire() > 0:
            limiter.set_rate(self.chats_default_capacity, self.chats_default_window)
            return
        logging.info(f'Rate Limiter triggered. Chat {update.chat.id}; User {update.from_user.id}')

        # Долгое действие, но пока запросов немного - ок
        if not await self._lamar_is_admin(update.chat.id):
            return

        # Увеличение окна до chats_default_window при текущих вводных
        limiter.set_rate(self.chats_default_capacity, 2 * self.chats_default_window - limiter.no_capacity_for())
        await self.bot.unban_chat_member(chat_id=update.chat.id,
                                         user_id=update.from_user.id,
                                         only_if_banned=False)
        

    async def _lamar_is_admin(self, chat_id: int):
        admins = await self.bot.get_chat_administrators(chat_id)
        return any(member.user.id == self.bot.user.id for member in admins)
        
