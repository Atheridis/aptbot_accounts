from aptbot.bot import Message, Commands, Bot
import os
import logging
from tools import smart_privmsg

logger = logging.getLogger(__name__)


PERMISSION = 99
PREFIX = "?"
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    if message.tags.get("reply-parent-display-name", None):
        smart_privmsg.send(
            bot,
            message,
            f"{message.tags['reply-parent-display-name']}, {message.nick} is UwUing you. Will you UwU back? PauseChamp",
            reply=message.tags["reply-parent-msg-id"],
        )
        return
    try:
        user = message.value.split(" ")[1]
    except IndexError:
        smart_privmsg.send(
            bot, message, f"UwU to you too {message.nick}!", reply=message.tags["id"]
        )
        return
    else:
        smart_privmsg.send(
            bot,
            message,
            f"{user}, {message.nick} is UwUing you. Will you UwU back? PauseChamp",
        )
        return
