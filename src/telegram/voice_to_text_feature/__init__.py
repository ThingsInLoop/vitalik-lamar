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

       
    def check_video(self, message):
        if message.text != self.lamar_tag and message.chat.type != 'private':
            return False

        return message.video_note is not None or (
               message.reply_to_message is not None and
               message.reply_to_message.video_note is not None)

    
    async def process_voice(self, message):
        if not await self._validate_user(message):
            return

        media_message = await self._get_media_message(message)
        if media_message is None:
            return
      
        assert media_message.voice is not None
        voice_bytes = await self._download(media_message.voice)

        text = await self.speechkit.recognize(voice_bytes)
        await self.bot.reply_to(media_message, f'"{text}"' if len(text.strip()) != 0 else '*Никто ничего не сказал*')

       
    async def process_video(self, message):
        if not await self._validate_user(message):
            return

        media_message = await self._get_media_message(message)
        if media_message is None:
            return
       
        assert media_message.video_note is not None
        video_bytes = await self._download(media_message.video_note)
        voice_bytes = utils.extract_audio(video_bytes) 
          
        text = await self.speechkit.recognize(voice_bytes)
        await self.bot.reply_to(media_message, f'"{text}"' if len(text.strip()) != 0 else '*Никто ничего не сказал*')


    async def _validate_user(self, message):
        if message.chat.type == 'private' and self.users.get_user(message.from_user.id) is None:
            await self.bot.reply_to(message, 'Я тебя еще не знаю. Чтобы я тебя запомнил, '
                                             'попиши что-то в чате, где есть я')
            return False
        return True
   
        
    async def _get_media_message(self, message):
        media = utils.choose_media(message)
        if media is None:
            message = message.reply_to_message
        media = utils.choose_media(message)
        assert media is not None
       
        if media.duration > self.file_len_cap:
            await self.bot.reply_to(message,
                                    f'Файл должен быть не более {self.file_len_cap} секунд')
            return None

        return message
        

    async def _download(self, media):
        url = await self.bot.get_file_url(media.file_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()
       
