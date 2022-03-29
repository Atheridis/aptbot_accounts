from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = ""
USER_COOLDOWN = 10
GLOBAL_COOLDOWN = 0


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    msg = (msg + ' ') * 10
    tools.smart_privmsg.send(bot, message, msg)
    # bot.send_privmsg(message.channel, msg)
