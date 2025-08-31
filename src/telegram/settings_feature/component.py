import telegram

from telegram.settings_feature.menu import Menu

class Component:
    name = 'settings-feature'

    @staticmethod
    def create(components, settings):
        self = Component()
        bot_component = components.find(telegram.BotComponent)
        self.menu = Menu(bot_component.get())

        bot_component.add_command_for_private_chats('chats', 'Настройки чатов')
        return self
