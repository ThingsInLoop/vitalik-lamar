import aiohttp

import telegram
import speech
import storage

import telegram.voice_to_text_feature.utils as utils


class Component:
    name = 'voice-to-text-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        users = components.find(storage.UsersComponent).get()
        bot = components.find(telegram.BotComponent).get()
        speechkit = components.find(speech.SpeechComponent).get()

        self.voice_to_text = VoiceToText(settings, bot, speechkit, users)
        return self


class VoiceToText:
    def __init__(self, settings, bot, speechkit, users):
        self.bot = bot
        self.speechkit = speechkit
        self.users = users
        self.lamar_tag = settings['lamar-tag']
        self.file_size_cap = settings.get('file-size-cap', 1024 * 1024)
        self.file_len_cap = settings.get('file-len-cap', 30)

        @bot.message_handler(func=self.check_voice, content_types=['text', 'voice'])
        async def voice_to_text_feature(message):
            await self.process_voice(message)

        @bot.message_handler(func=self.check_video, content_types=['text', 'video_note'])
        async def video_to_text_feature(message):
            await self.process_video(message)
        

    def check_voice(self, message):
        if message.text != self.lamar_tag and message.chat.type != 'private':
            return False

        return message.voice is not None or (
               message.reply_to_message is not None and
               message.reply_to_message.voice is not None)

    
    async def process_voice(self, message):
        if self.users.get_user(message.from_user.id) is None:
            await self.bot.reply_to(message, 'Я тебя еще не знаю. Чтобы я тебя запомнил, '
                                             'попиши что-то в чате, где есть я')
            return
                    
        if message.voice is None:
            message = message.reply_to_message

        if message.voice.file_size > self.file_size_cap:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не больше {self.file_size_cap} байт')
            return

        if message.voice.duration > self.file_len_cap:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не длиннее {self.file_len_cap} секунд')         
            return
       
        voice_url = await self.bot.get_file_url(message.voice.file_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(voice_url) as response:
                voice_file = await response.read()

        text = await self.speechkit.recognize(voice_file)
        await self.bot.reply_to(message, text if len(text.strip()) != 0 else '*Никто ничего не сказал*')


    def check_video(self, message):
        if message.text != self.lamar_tag and message.chat.type != 'private':
            return False

        return message.video_note is not None or (
               message.reply_to_message is not None and
               message.reply_to_message.video_note is not None)

       
    async def process_video(self, message):
        if self.users.get_user(message.from_user.id) is None:
            await self.bot.reply_to(message, 'Я тебя еще не знаю. Чтобы я тебя запомнил, '
                                             'попиши что-то в чате, где есть я')
            return
                    
        original_message = message
        if message.video_note is None:
            message = message.reply_to_message

        if message.video_note.file_size > self.file_size_cap * 10:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не больше {self.file_size_cap} байт')
            return

        if message.video_note.duration > self.file_len_cap:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не длиннее {self.file_len_cap} секунд')
            return
       
        video_note_url = await self.bot.get_file_url(message.video_note.file_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(video_note_url) as response:
                video_note_bytes = await response.read()

        voice_bytes = utils.extract_audio(video_note_bytes, original_message.from_user.id) 
          
        if len(voice_bytes) > self.file_size_cap:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не больше {self.file_size_cap} байт')
            return
            
        text = await self.speechkit.recognize(voice_bytes)
        await self.bot.reply_to(message, text if len(text.strip()) != 0 else '*Никто ничего не сказал*')
