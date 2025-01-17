from enum import Enum


class UserVerification(Enum):
    verified = 'verified'
    banned = 'banned'


class Users:
    def __init__(self, users_storage, messages_storage):
        self.unverified_users = dict()
        self.verified_users  = set()
        self.banned_users    = set()

        self._users_storage = users_storage
        self._messages_storage = messages_storage
        for user in users_storage.read_users_by_verification(
            UserVerification.verified.value
        ):
            self.verified_users.add(int(user[0]))
        for user in users_storage.read_users_by_verification(
            UserVerification.banned.value
        ):
            self.banned_users.add(int(user[0]))

    def get_username(self, user_id: int):
        user = self._users_storage.get_user(user_id)
        if user is None:
            return None
        return ('@' + user[2]) if user[2] is not None else user[1]

    def is_verified(self, user):
        return user.id in self.verified_users

    def is_banned(self, user):
        return user.id in self.banned_users

    def verify(self, user):
        verifications = self.unverified_users.get(user.id, 0) + 1
        self.unverified_users[user.id] = verifications
        if verifications < 3:
            return
        self._users_storage.add_user(
            user.id,
            user.first_name,
            user.username,
            UserVerification.verified.value)
        self.unverified_users.pop(user.id, None)
        self.verified_users.add(user.id)
        
    def ban(self, for_message):
        self._users_storage.add_user(
            for_message.from_user.id,
            for_message.from_user.first_name,
            for_message.from_user.username,
            UserVerification.banned.value)
        self._users_storage.update_ban_message(
            for_message.from_user.id,
            for_message.message_id,
            for_message.chat.id)
        self._messages_storage.write_message(
            for_message.message_id,
            for_message.chat.id,
            for_message.text)

        self.unverified_users.pop(for_message.from_user.id, None)
        self.banned_users.add(for_message.from_user.id)

    def pardon(self, user_id: int):
        self._users_storage.update_verification(user_id, UserVerification.verified.value)
        self.unverified_users.pop(user_id, None)
        self.banned_users.discard(user_id)
        self.verified_users.add(user_id)
 
