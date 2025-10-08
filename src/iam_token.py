import aiohttp
import asyncio
import json
import requests
import logging


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
            self.iam_token = requests.post(self.url, data=json.dumps(self.request)).json()['iamToken']
        except Exception as e:
            logging.error(f'Exception on attempt to get IAM_TOKEN: {e}')
            raise e

    def get(self):
        return self.iam_token

    async def async_token(self):
        logging.info('Update IAM_TOKEN')
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=json.dumps(self.request)) as response:
                return (await response.json())['iamToken']

    async def polling(self):
        while True:
            try:
                self.iam_token = await self.async_token()
                logging.info('Got new IAM_TOKEN')
                await asyncio.sleep(3600)
            except Exception as e:
                logging.error(f'Exception on attempt to update IAM_TOKEN: {e}')
            finally:
                await asyncio.sleep(1)

