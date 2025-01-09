import sqlite3
import sys


class Component:
    name = 'messages-storage'

    @staticmethod
    def create(components, settings):
        self = Component()
        self.storage = Messages(settings)
        return self

    def get(self):
        return self.storage


class Messages:
    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages(id, chat_id, message)
  """

    insert_message = """
    INSERT INTO messages VALUES 
      ('{}', '{}', '{}')
  """

    select_messages = """
    SELECT * FROM messages
  """

    def __init__(self, settings):
        path_to_db = settings["storage"]["db-path"]
        self.connection = sqlite3.connect(path_to_db)
        cursor = self.connection.cursor()
        cursor.execute(self.create_messages_table)

    def write_message(self, message_id, chat_id, message_text):
        cursor = self.connection.cursor()
        cursor.execute(self.insert_message.format(message_id, chat_id, message_text))
        self.connection.commit()

    def read_messages(self):
        cursor = self.connection.cursor()
        result = cursor.execute(self.select_messages)
        return [i for i in result.fetchall()]


if __name__ == "__main__":
    db = Messages({"storage": {"db-path": sys.argv[1]}})

    print(db.read_messages())

