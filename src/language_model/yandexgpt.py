import asyncio
import json

from yandex_cloud_ml_sdk import YCloudML

from language_model.iam_token import Token
from language_model.iam_token import iam_token_polling
from language_model.fishing_samples import fishing_samples


class Model:
  def __init__(self, config_component):
    self.config_component = config_component
    settings = config_component.get_config()['language-model']['yandexgpt']

    self.yc_folder_id = settings['folder-id']
    self.token = Token(settings['oauth'])

  async def start(self):
    await iam_token_polling(self.token)

  async def is_fishing(self, message: str):
    iam_token = await self.token.get()
    sdk = YCloudML(folder_id=self.yc_folder_id, auth=iam_token)

    model = sdk.models.text_classifiers("yandexgpt").configure(
      task_description="Определи категорию сообщения, отправленного в чат бегового клуба",
      labels=['фишинг', 'прочее'],
      samples=fishing_samples,
    )

    result = model.run(message)

    for prediction in result:
      if prediction.confidence >= 0.92 and prediction.label == 'фишинг':
        return True

    return False

  async def get_answer(self, message: str):
    iam_token = await self.token.get()
    sdk = YCloudML(folder_id=self.yc_folder_id, auth=iam_token)

    model = sdk.models.completions('yandexgpt').configure(temperature=1.0)

    result = model.run(message)

    return result.alternatives[0].text
