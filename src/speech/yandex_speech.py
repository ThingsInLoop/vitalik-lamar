import tempfile
import asyncio
import concurrent.futures

from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType

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
        self.folder_id = settings['folder-id']
        
    async def recognize(self, audio):
        iam_token = self.token.get()
        configure_credentials(
           yandex_credentials=creds.YandexCredentials(
              iam_token=iam_token,
              folder_id=self.folder_id,
           )
        )
        
        model = model_repository.recognition_model()

        model.model = 'general'
        model.language = 'ru-RU'
        model.audio_processing_type = AudioProcessingType.Full

        with tempfile.NamedTemporaryFile() as file:
            file.write(audio)
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, model.transcribe_file, file.name)

        return str(result[0])
