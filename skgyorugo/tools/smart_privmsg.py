from aptbot.bot import Bot, Message, Commands

MAX_LENGTH = 469


def _split_message(message: str) -> list[str]:
    split_count = len(message) // MAX_LENGTH + 1
    words = message.split(' ')
    word_list = [''] * split_count
    index = 0
    for word in words:
        if len(word_list[index]) >= MAX_LENGTH:
            index += 1
        word_list[index] += word + ' '

    return word_list


def send(bot: Bot, message_data: Message, message: str, to_remove: int = 1):
    # for msg in _split_message(' '.join(message_data.value.split(' ')[1:])):
    #     message = message.replace("{message}", msg)
    #     message = message.replace("{nick}", message_data.nick)
    #     message = message.replace("{channel}", message_data.channel)
    msg = ' '.join(message_data.value.split(' ')[to_remove:])
    message = message.replace("{message}", msg)
    message = message.replace("{nick}", message_data.nick)
    message = message.replace("{channel}", message_data.channel)

    messages = _split_message(message)
    bot.send_privmsg(message_data.channel, messages)
