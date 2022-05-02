from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = ""
USER_COOLDOWN = 30
GLOBAL_COOLDOWN = 15

MAX_LENGTH = 450


def main(bot: Bot, message: Message):
    try:
        replied_message = message.tags["reply-parent-msg-body"]
    except KeyError:
        replied_message = None
    if replied_message:
        msg = replied_message
    else:
        msg = ' '.join(message.value.split(' ')[1:])
    new_msg = ""
    while len(new_msg) + len(msg) < MAX_LENGTH:
        new_msg += msg + " "
    tools.smart_privmsg.send_safe(bot, message.channel, new_msg)
