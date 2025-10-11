import logging

from yandex_cloud_ml_sdk import AsyncYCloudML

import iam_token
from language_model.fishing_samples import fishing_samples


class Component:
    name = 'language-model'

    @staticmethod
    def create(components, settings):
        self = Component()
        token = components.find(iam_token.Component).get()
        self.model = Model(settings, token)
        return self

    def get(self):
        return self.model


labels=['фишинг', 'прочее']

class Model:
    def __init__(self, settings, token):
        settings = settings['yandexgpt']
        self.yc_folder_id = settings['folder-id']
        self.token = token
        self.fishing_enough_confidence = settings.get('fishing-enough-confidence', 0.8)

    async def is_fishing(self, message: str):
        iam_token = self.token.get()
        sdk = AsyncYCloudML(folder_id=self.yc_folder_id, auth=iam_token, verify=False)

        model = sdk.models.text_classifiers('yandexgpt-lite').configure(
            task_description='Определи категорию сообщения, отправленного в чат бегового клуба',
            labels=labels,
            samples=fishing_samples,
        )

        try:
            result = await model.run(message)
        except Exception as e:
            logging.error(f'Exception while trying to get prediction: {e}')
            return False

        for prediction in result:
            logging.info(f'{prediction}')

            if (prediction.confidence >= self.fishing_enough_confidence and
                prediction.label in (labels[0])
            ):
                return True

        return False

    async def prompt(self, message: str):
        iam_token = self.token.get()
        sdk = AsyncYCloudML(folder_id=self.yc_folder_id, auth=iam_token)

        model = sdk.models.completions('yandexgpt').configure(temperature=1.0)

        result = await model.run(message)

        return result.alternatives[0].text
