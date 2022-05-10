from aptbot.bot import Bot, Message, Commands
from typing import Union

MAX_LENGTH = 480


def _split_message(message: str) -> list[str]:
    split_count = len(message) // MAX_LENGTH + 1
    words = message.split(" ")
    word_list = [""] * split_count
    index = 0
    for word in words:
        if len(word_list[index]) >= MAX_LENGTH:
            index += 1
        word_list[index] += word + " "

    return word_list


def send_safe(bot: Bot, channel: str, messages: Union[str, list], reply=None):
    if isinstance(messages, list):
        for i in range(len(messages)):
            while True:
                if (
                    messages[i].startswith("/")
                    or messages[i].startswith("!")
                    or messages[i].startswith("\\")
                    or messages[i].startswith("?")
                ):
                    messages[i] = messages[i][1:]
                else:
                    break
    else:
        while True:
            if (
                messages.startswith("/")
                or messages.startswith("!")
                or messages.startswith("\\")
                or messages.startswith("?")
            ):
                messages = messages[1:]
            else:
                break
    bot.send_privmsg(channel, messages, reply)


def send(
    bot: Bot,
    message_data: Message,
    message: str,
    to_remove: int = 1,
    safe_send: bool = True,
    reply=None,
):
    # for msg in _split_message(' '.join(message_data.value.split(' ')[1:])):
    #     message = message.replace("{message}", msg)
    #     message = message.replace("{nick}", message_data.nick)
    #     message = message.replace("{channel}", message_data.channel)
    msg = " ".join(message_data.value.split(" ")[to_remove:])
    message = message.replace("{message}", msg)
    message = message.replace("{nick}", message_data.nick)
    message = message.replace("{channel}", message_data.channel)

    messages = _split_message(message)
    if safe_send:
        send_safe(bot, message_data.channel, messages, reply)
    else:
        bot.send_privmsg(message_data.channel, messages, reply)
