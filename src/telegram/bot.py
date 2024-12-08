import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.util import quick_markup


class Bot:
  def __init__(self, config_component, lang_model, messages_storage):
    self.config_component = config_component
    settings = config_component.get_config()['telegram-bot']

    self.bot = AsyncTeleBot(settings['token'])
    self.lang_model = lang_model
    self.messages = messages_storage

    @self.bot.callback_query_handler(
      func=lambda callback: callback.data == 'фишинг' or callback.data == 'прочее'
    )
    async def callbacks(callback):
      await self.remove_markup(callback.message)

      if callback.data == 'прочее':
        self.messages.write_message('прочее', callback.message.reply_to_message.text)
        await self.send_apologizes(callback.message.reply_to_message)
        return

      self.messages.write_message('фишинг', callback.message.reply_to_message.text)
      await self.send_gratitude(callback)


    @self.bot.message_handler(func=lambda message: True)
    async def chats_messages(message):
      if not await lang_model.is_fishing(message.text):
        return

      markup = quick_markup({
        'Ага': {'callback_data': 'фишинг'},
        'Неа': {'callback_data': 'прочее'},
      }, row_width=2)

      await self.bot.reply_to(message, 'Это спам?', reply_markup=markup)

  async def start(self):
    await self.bot.polling()

  async def remove_markup(self, message):
    await self.bot.edit_message_reply_markup(
      message.chat.id,
      message.message_id,
      reply_markup=None
    )   

  async def send_apologizes(self, for_message):
    apologizes = await self.lang_model.get_answer(
      """
        Ты перепутал, и обвинил друга {} в отправке спама. Кратко и с отмазкой извинись.
        Используй имя в его краткой форме на русском языке.
      """.format(for_message.from_user.first_name)
    )

    await self.bot.reply_to(for_message, apologizes)

  async def send_gratitude(self, for_callback):
    gratitude = await self.lang_model.get_answer(
      """
        Ты угадывал какое сообщение спам, а какое не спам. Друг {} помог тебе определить спам.
        Кратко и мило поблагодари друга и, если захочешь, остальных ребят из чата.
        Используй имя в его краткой форме и на русском языке.
      """.format(for_callback.from_user.first_name)
    )

    await self.bot.reply_to(for_callback.message, gratitude)

