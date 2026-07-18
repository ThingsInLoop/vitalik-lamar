import asyncio
import json
import logging
import time
import jwt

import yandexcloud

from yandex.cloud.iam.v1.iam_token_service_pb2 import (CreateIamTokenRequest)
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub


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


def create_iam_token(key_path: str):
    with open(key_path, 'r') as f:
        obj = f.read() 
        obj = json.loads(obj)
        private_key = obj['private_key']
        key_id = obj['id']
        service_account_id = obj['service_account_id']

    sa_key = {
        "id": key_id,
        "service_account_id": service_account_id,
        "private_key": private_key
    }
    now = int(time.time())
    payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': service_account_id,
            'iat': now,
            'exp': now + 3600
        }

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    sdk = yandexcloud.SDK(service_account_key=sa_key)
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
      CreateIamTokenRequest(jwt=encoded_token)
    )

    return iam_token.iam_token


class Token:
    def __init__(self, settings):
        self.iam_token = None
        self.key_path = settings['key-path']
        try:
            self.iam_token = create_iam_token(self.key_path)
        except Exception as e:
            logging.error(f'Exception on attempt to get IAM_TOKEN: {e}')
            raise e

    def get(self):
        return self.iam_token

    async def async_token(self):
        logging.info('Update IAM_TOKEN')
        return await asyncio.to_thread(create_iam_token, self.key_path)

    async def polling(self):
        await asyncio.sleep(1800)
        while True:
            try:
                new_token = await self.async_token()
                if new_token is None:
                    raise ValueError('New async token is None')
                self.iam_token = new_token
                logging.info(f'Got new IAM_TOKEN: {self.iam_token}')
                await asyncio.sleep(1800)
            except Exception as e:
                logging.error(f'Exception on attempt to update IAM_TOKEN: {e}')
            finally:
                await asyncio.sleep(1)

