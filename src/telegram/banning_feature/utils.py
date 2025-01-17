from telebot.util import quick_markup


def pardon_markup(text, message):
    callback_data = {
        'type': 'banning-pardon',
        'user_id': message.from_user.id,
    }
    return quick_markup(
        {
            text: {
                'callback_data': str(callback_data)
            },
        },
        row_width=1,
    )


def too_many_custom_emojis(message):
    if message.entities is None:
        return False

    custom_emojis = sum(1 for entity in message.entities if entity.type == 'custom_emoji')
    if custom_emojis > 20:
        return True
