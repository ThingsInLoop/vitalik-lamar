import telegram
import speech
import aiohttp


class Component:
    name = 'voice-to-text-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        bot = components.find(telegram.BotComponent).get()
        speechkit = components.find(speech.SpeechComponent).get()

        self.voice_to_text = VoiceToText(settings, bot, speechkit)
        return self


class VoiceToText:
    def __init__(self, settings, bot, speechkit):
        self.bot = bot
        self.speechkit = speechkit
        self.lamar_tag = settings['lamar-tag']
        self.voice_size_cap = settings.get('voice-size-cap', 1024 * 1024)

        @bot.message_handler(func=self.check_message)
        async def voice_to_text_feature(message):
            await self.process_message(message)


    def check_message(self, message):
        if message.text != self.lamar_tag:
            return False
        
        return (message.reply_to_message is not None and
                message.reply_to_message.voice is not None and
                message.reply_to_message.voice.file_size < self.voice_size_cap)


    async def process_message(self, message):
        voice_url = await self.bot.get_file_url(message.reply_to_message.voice.file_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(voice_url) as response:
                voice_file = await response.read()

        text = await self.speechkit.recognize(voice_file)
        await self.bot.reply_to(message.reply_to_message, text)

