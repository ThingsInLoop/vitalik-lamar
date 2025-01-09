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

    def get_users(self):
        return self.users

    def get_messages(self):
        return self.messages

