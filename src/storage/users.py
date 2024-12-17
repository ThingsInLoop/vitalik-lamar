import sqlite3
import json
import sys


class Users:
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users(id, first_name, username, verification, banned_for_message)
  """

    insert_new_user = """
    INSERT INTO users VALUES 
      ('{}', '{}', '{}', '{}', NULL)
  """

    insert_new_user_wout_username = """
    INSERT INTO users VALUES 
      ('{}', '{}', NULL, '{}', NULL)
  """

    select_user_by_id = """
    SELECT * from users
    WHERE id == '{}'
  """

    update_verification_query = """
    UPDATE users
    SET verification = '{}'
    WHERE id == '{}'
  """

    update_banned_for_message = """
    UPDATE users
    SET banned_for_message = '{}'
    WHERE id == '{}'
  """

    select_all_users = """
    SELECT * FROM users
  """

    select_users_by_verification = """
    SELECT id, username, banned_for_message FROM users
    WHERE verification == '{}'
  """

    def __init__(self, config_component):
        self.config_component = config_component
        path_to_db = config_component.get_config()["storage"]["db-path"]

        self.connection = sqlite3.connect(path_to_db)
        cursor = self.connection.cursor()
        cursor.execute(self.create_users_table)

    def add_user(self, user_id, first_name, username, verification):
        cursor = self.connection.cursor()
        if username is not None:
            cursor.execute(self.insert_new_user.format(
                user_id,
                first_name,
                username,
                verification))
        else:
            cursor.execute(self.insert_new_user_wout_username.format(
                user_id,
                first_name,
                verification))
        self.connection.commit()

    def get_user(self, user_id):
        cursor = self.connection.cursor()
        result = cursor.execute(self.select_user_by_id.format(user_id))
        return result.fetchone()

    def update_verification(self, user_id, new_verification):
        cursor = self.connection.cursor()
        cursor.execute(self.update_verification_query.format(new_verification, user_id))
        self.connection.commit()

    def update_ban_message(self, user_id, message_id, chat_id):
        ban_for_message = {'message_id': message_id, 'chat_id': chat_id}

        cursor = self.connection.cursor()
        cursor.execute(self.update_banned_for_message.format(json.dumps(ban_for_message), user_id))
        self.connection.commit()

    def read_users(self):
        cursor = self.connection.cursor()
        result = cursor.execute(self.select_all_users)
        return [i for i in result.fetchall()]

    def read_users_by_verification(self, verification):
        cursor = self.connection.cursor()
        result = cursor.execute(self.select_users_by_verification.format(verification))
        return [i for i in result.fetchall()]


class ConfigMock:
    def get_config(self):
        return {"storage": {"db-path": sys.argv[1]}}


if __name__ == "__main__":
    config_mock = ConfigMock()
    db = Users(config_mock)

    print(db.read_users())

