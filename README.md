# vitalik-lamar

python dependencies:
 - pyyaml
 - pyTelegramBotAPI
 - yandex-cloud-ml-sdk
 - yandex-speechkit (с изменениями для folder_id)
 - pytest-asyncio
 - moviepy


 components schema:

 ```mermaid
 flowchart TD
    voice-to-text-feature;
    speech;
    ping-feature;
    banning-feature;
    storage;
    language-model;
    telegram-bot;
    iam-token;
    messages-storage;
    users-storage;
    voice-to-text-feature --> speech;
    voice-to-text-feature --> telegram-bot;
    voice-to-text-feature --> users-storage;
    speech --> iam-token;
    ping-feature --> telegram-bot;
    banning-feature --> speech;
    banning-feature --> language-model;
    banning-feature --> storage;
    banning-feature --> telegram-bot;
    storage --> messages-storage;
    storage --> users-storage;
    language-model --> iam-token;
```
