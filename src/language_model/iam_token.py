import asyncio
import json
import copy

import requests


class Token:
    iam_token = None
    lock = asyncio.Lock()

    def __init__(self, oauth):
        self.url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        self.request = {"yandexPassportOauthToken": oauth}
        try:
            response = requests.post(self.url, data=json.dumps(self.request))
            self.iam_token = response.json()["iamToken"]
        finally:
            pass

    async def get(self):
        async with self.lock:
            return copy.deepcopy(self.iam_token)

    async def update(self):
        response = requests.post(self.url, data=json.dumps(self.request))
        async with self.lock:
            self.iam_token = response.json()["iamToken"]


async def iam_token_polling(token: Token):
    while True:
        try:
            await token.update()
            await asyncio.sleep(3600)
        finally:
            await asyncio.sleep(5)
