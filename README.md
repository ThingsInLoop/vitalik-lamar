# vitalik-lamar

**python dependencies**:
 - pyyaml
 - pyTelegramBotAPI
 - yandex-cloud-ml-sdk
 - yandex-speechkit (с изменениями для folder_id)
 - pytest-asyncio
 - moviepy


**components flowchart**:

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
    telegram-bot --> voice-to-text-feature;
    speech --> voice-to-text-feature;
    iam-token --> speech;
    telegram-bot --> ping-feature;
    storage --> banning-feature;
    language-model --> banning-feature;
    telegram-bot --> banning-feature;
    speech --> banning-feature;
    users-storage --> storage;
    messages-storage --> storage;
    iam-token --> language-model;
```
