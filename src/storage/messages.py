import sqlite3


class Messages:
    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages(type, message)
  """

    insert_message = """
    INSERT INTO messages VALUES 
      ('{}', '{}')
  """

    select_messages_by_type = """
    SELECT message FROM messages
    WHERE type == '{}'
  """

    def __init__(self, config_component):
        self.config_component = config_component
        path_to_db = config_component.get_config()["storage"]["db-path"]

        self.connection = sqlite3.connect(path_to_db)
        cursor = self.connection.cursor()
        cursor.execute(self.create_messages_table)

    def write_message(self, message_type, message_text):
        cursor = self.connection.cursor()
        cursor.execute(self.insert_message.format(message_type, message_text))
        self.connection.commit()

    def read_messages(self, message_type):
        cursor = self.connection.cursor()
        result = cursor.execute(self.select_messages_by_type.format(message_type))
        return [i[0] for i in result.fetchall()]


class ConfigMock:
    def get_config(self):
        return {"storage": {"db-path": "/home/oltermanni/vitalik-lamar-messages.db"}}


if __name__ == "__main__":
    config_mock = ConfigMock()
    db = Messages(config_mock)
    fishing = db.read_messages("фишинг")
    other = db.read_messages("прочее")

    print("other: ", len(other), "; fishing: ", len(fishing), "\n")

    written = {}
    for message in fishing:
        if message in written:
            continue
        print({"text": message, "label": "фишинг"})
        written[message] = True

    print("\n")

    for message in other:
        if message in written:
            continue
        print({"text": message, "label": "прочее"})
        written[message] = True
