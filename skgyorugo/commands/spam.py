from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = ""
USER_COOLDOWN = 10
GLOBAL_COOLDOWN = 0

MAX_LENGTH = 469


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    new_msg = ""
    while len(new_msg) + len(msg) > MAX_LENGTH:
        new_msg += msg + " "
    bot.send_privmsg(message.channel, msg)
