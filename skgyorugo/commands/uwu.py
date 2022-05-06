from aptbot.bot import Message, Commands, Bot
import os
import logging
from tools import smart_privmsg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)


PERMISSION = 99
PREFIX = '?'
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    if message.tags.get("reply-parent-display-name", None):
        smart_privmsg.send(bot, message, f"UwU {message.tags['reply-parent-display-name']}", reply=message.tags['reply-parent-msg-id'])
        return
    try:
        user = message.value.split(' ')[1]
    except IndexError:
        smart_privmsg.send(bot, message, f"UwU to you too {message.nick}!")
        return
    else:
        smart_privmsg.send(bot, message, f"{user}, {message.nick} is UwUing you. Will you UwU back? PauseChamp")
        return
