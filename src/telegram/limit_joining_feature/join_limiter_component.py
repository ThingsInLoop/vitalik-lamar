import datetime
import logging
import asyncio

import telegram
import utils

class JoinLimiterComponent:
    name = 'join-limiter-feature'

    @staticmethod
    def create(components, settings):
        self = JoinLimiterComponent()

        self.rate_limited_users = {}
        self.join_messages = {}
        self.chats_limiters = {}
        self.rate_limit_notifications = {}
        
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

        @self.bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
        async def notification_handler(message):
            await self.process_notification(message)

        return self

    def stop(self):
        for _, task in self.rate_limit_notifications.items():
            task.cancel()

    async def process_notification(self, message):
        logging.debug('Processing join notification')
        
        if message.left_chat_member is not None and message.from_user.id == self.bot.user.id:
            logging.debug('Deleting user\'s removal via bot message')
            await self.bot.delete_message(message.chat.id, message.message_id)
            return
        if message.new_chat_members is None:
            return

        if message.chat.id in self.rate_limited_users:
            for member in message.new_chat_members:
                if member.id in self.rate_limited_users[message.chat.id]:
                    try:
                        logging.debug('Deleting rate limited user\'s join message. Notification processing')
                        await self.bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        logging.warning(f'Can\'t delete message {message.message_id} from chat {message.chat.id}: {e}')
        
        chat_joins = self.join_messages.setdefault(message.chat.id, dict())
        for member in message.new_chat_members:
            chat_joins[member.id] = message
        

    async def process_new_chat_member(self, update):
        logging.debug('Processing new chat member')
        
        limiter = self.chats_limiters.setdefault(
            update.chat.id,
            utils.SlidingWindowRateLimiter(
                self.chats_default_capacity,
                self.chats_default_window
            )
        )

        if limiter.acquire() > 0:
            limiter.set_rate(self.chats_default_capacity, self.chats_default_window)
            self.rate_limited_users.clear()
            self.join_messages.clear()
            return
        logging.info(f'Rate Limiter triggered. Chat {update.chat.id}; User {update.from_user.id}')

        await self._trigger_rate_limit(limiter, update)


    async def _trigger_rate_limit(self, limiter, update):
        # Долгое действие, но пока запросов немного - ок
        if not await self._lamar_is_admin(update.chat.id):
            return

        # Увеличение окна до chats_default_window при текущих вводных
        _, window = limiter.get_rate()
        limiter.set_rate(self.chats_default_capacity, window + self.chats_default_window - limiter.no_capacity_for())
        await self.bot.unban_chat_member(chat_id=update.chat.id,
                                         user_id=update.from_user.id,
                                         only_if_banned=False)

        self.rate_limited_users.setdefault(update.chat.id, set()).add(update.from_user.id)
        if update.chat.id in self.join_messages and update.from_user.id in self.join_messages[update.chat.id]:
            try:
                logging.debug('Deleting rate limited user\'s join message. New chat member processing')
                message_id = self.join_messages[update.chat.id][update.from_user.id].message_id
                self.join_messages[update.chat.id].pop(update.from_user.id)
                await self.bot.delete_message(update.chat.id, message_id)
            except Exception as e:
                logging.warning(f'Can\'t delete message {self.join_messages[update.chat.id][update.from_user.id].message_id}'
                                f' from chat {update.chat.id}: {e}')

        if (update.chat.id in self.rate_limit_notifications and
            not (self.rate_limit_notifications[update.chat.id].done() or
             self.rate_limit_notifications[update.chat.id].cancelled())):
            return
        self.rate_limit_notifications[update.chat.id] = asyncio.create_task(self._notify(update.chat))


    async def _notify(self, chat):
        limiter = self.chats_limiters.setdefault(
            chat.id,
            utils.SlidingWindowRateLimiter(
                self.chats_default_capacity,
                self.chats_default_window
            )
        )
        message = await self.bot.send_message(chat.id, 'Временно нельзя вступать в чат')

        while limiter.no_capacity_for() != datetime.timedelta(seconds=0):
            logging.debug(f'Check rate limiter capacity in chat {chat.id}: {limiter.no_capacity_for()}')
            await asyncio.sleep(1)

        await self.bot.delete_message(chat.id, message.message_id)
        

    async def _lamar_is_admin(self, chat_id: int):
        admins = await self.bot.get_chat_administrators(chat_id)
        return any(member.user.id == self.bot.user.id for member in admins)
        
