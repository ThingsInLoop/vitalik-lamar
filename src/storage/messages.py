import sqlite3
import sys


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

    def __init__(self, config_component):
        self.config_component = config_component
        path_to_db = config_component.get_config()["storage"]["db-path"]

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


class ConfigMock:
    def get_config(self):
        return {"storage": {"db-path": sys.argv[1]}}


if __name__ == "__main__":
    config_mock = ConfigMock()
    db = Messages(config_mock)

    print(db.read_messages())

