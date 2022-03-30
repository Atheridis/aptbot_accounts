from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import scripts.translator

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = "Translates a message from any language (supported by google translate) into English. How to use: ?t <insert text to translate>"
USER_COOLDOWN = 15
GLOBAL_COOLDOWN = 5


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    trans = scripts.translator.translate(msg)
    tools.smart_privmsg.send(bot, message, trans)
