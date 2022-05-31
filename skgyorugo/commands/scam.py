from aptbot.bot import Message, Commands, Bot

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = ""
USER_COOLDOWN = 10
GLOBAL_COOLDOWN = 10


def main(bot: Bot, message: Message):
    msg = message.nick + " you have been scammed KEKW"
    bot.send_privmsg(message.channel, msg)
