import asyncio
import json
import concurrent.futures

import requests


class Component:
    name = 'iam-token'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.token = Token(settings)
        self.polling = asyncio.create_task(self.token.polling())
        return self

    def get(self):
        return self.token


class Token:
    def __init__(self, settings):
        self.iam_token = None
        self.url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        self.request = {"yandexPassportOauthToken": settings['oauth']}
        try:
            self.iam_token = self.update()
        finally:
            pass

    async def get(self):
        return self.iam_token

    def update(self):
        return requests.post(self.url, data=json.dumps(self.request)).json()['iamToken']

    async def polling(self):
        while True:
            try:
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    self.iam_token = await loop.run_in_executor(pool, self.update)
                await asyncio.sleep(3600)
            finally:
                await asyncio.sleep(5)

