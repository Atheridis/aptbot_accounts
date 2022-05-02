from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import scripts.translator

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = "Translates a message from any language (supported by google translate) into English. How to use: ?t <insert text to translate>"
USER_COOLDOWN = 15
GLOBAL_COOLDOWN = 5


def main(bot: Bot, message: Message):
    try:
        replied_message = message.tags["reply-parent-msg-body"]
    except KeyError:
        replied_message = None
    if replied_message:
        msg = replied_message
        replied_msg_id = message.tags["reply-parent-msg-id"]
    else:
        msg = ' '.join(message.value.split(' ')[1:])
        replied_msg_id = None
    trans = scripts.translator.translate(msg)
    print(trans)
    tools.smart_privmsg.send(bot, message, trans, reply=replied_msg_id)
