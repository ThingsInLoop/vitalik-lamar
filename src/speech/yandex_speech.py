import tempfile
import asyncio
import concurrent.futures

from yandex_ai_studio_sdk import AsyncAIStudio

import iam_token


class Component:
    name = 'speech'

    @staticmethod
    def create(components, settings):
        self = Component()
        token = components.find(iam_token.Component).get()
        self.speech = YandexSpeech(token, settings['yandex-speechkit'])
        return self

    def get(self):
        return self.speech


class YandexSpeech:
    def __init__(self, token, settings):
        self.token = token
        self.yc_folder_id = settings['folder-id']
        
    async def recognize(self, audio):
        iam_token = self.token.get()

        sdk = AsyncAIStudio(folder_id=self.yc_folder_id, auth=iam_token)
        stt = sdk.speechkit.speech_to_text(
            audio_format=sdk.speechkit.AudioFormat.MP3,
            language_codes='ru_RU',
            text_normalization=True
        )
        result = await stt.run(audio)

        return result.text if result.text is not None else ""
