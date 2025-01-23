import aiohttp
import json

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
        self.recognition_url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
        
    async def recognize(self, audio):
        iam_token = self.token.get()
        headers = {'Authorization': f'Bearer {iam_token}'}
        params = {
            'lang': 'ru-RU',
            'folderId': self.folder_id,
            'format': 'oggopus',
        }

        with open('/var/tmp/file.ogg', 'wb') as file:
            file.write(audio)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.recognition_url, params=params, data=audio) as response:
                return json.loads(await response.text())['result']

