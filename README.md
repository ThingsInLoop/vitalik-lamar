# vitalik-lamar

*python dependencies*:
 - pyyaml
 - pyTelegramBotAPI
 - yandex-cloud-ml-sdk
 - yandex-speechkit (с изменениями для folder_id)
 - pytest-asyncio
 - moviepy


 *components flowchart*:

 ```mermaid
flowchart TD
    speech;
    ping-feature;
    banning-feature;
    storage;
    language-model;
    telegram-bot;
    iam-token;
    messages-storage;
    users-storage;
    iam-token --> speech;
    telegram-bot --> ping-feature;
    telegram-bot --> banning-feature;
    language-model --> banning-feature;
    storage --> banning-feature;
    speech --> banning-feature;
    messages-storage --> storage;
    users-storage --> storage;
    iam-token --> language-model;
```
