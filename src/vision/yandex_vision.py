import base64
import aiohttp
import json
import logging

import iam_token

class Component:
    name = 'vision'

    @staticmethod
    def create(components, settings):
        self = Component()
        token = components.find(iam_token.Component).get()
        self.vision = YandexVision(token, settings['yandex-vision'])
        return self

    def get(self):
        return self.vision


class YandexVision:
    def __init__(self, token, settings):
        self.token = token
        self.folder_id = settings['folder-id']
        
    async def extract_text(self, image, mime_type):
        iam_token = self.token.get()

        content = base64.b64encode(image).decode('utf-8')

        data = {"mimeType": mime_type,
                "languageCodes": ["ru","en"],
                "content": content}

        url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

        headers= {"Content-Type": "application/json",
                  "Authorization": "Bearer {:s}".format(self.token.get()),
                  "x-folder-id": self.folder_id,
                  "x-data-logging-enabled": "true"}
  
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), headers=headers) as response:
                answer = await response.json()
                return answer['result']['textAnnotation']['fullText']
