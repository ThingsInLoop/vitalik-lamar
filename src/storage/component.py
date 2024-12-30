from storage import UsersComponent
from storage import MessagesComponent


class Component:
    name = 'storage'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.users = components.find(UsersComponent).get()
        self.messages = components.find(MessagesComponent).get()
        return self

    def users(self):
        return self.users

    def messages(self):
        return self.messages

