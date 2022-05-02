from aptbot.bot import Bot, Message, Commands
import tools.smart_privmsg
import random


def chatting(bot: Bot, message: Message):
    if "Chatting" not in message.value:
        return
    if random.random() > 0.4:
        return
    msg = ""
    if "reply-parent-msg-body" in message.tags:
        if message.value.split(' ')[1] == "Chatting":
            msg = ' '.join(message.value.split(' ')[1:])
    else:
        if message.value.split(' ')[0] == "Chatting":
            msg = message.value
    if msg:
        tools.smart_privmsg.send(bot, message, msg)


def chatting_annoy(bot: Bot, message: Message):
    nicks = {}
    if message.nick.lower() not in nicks:
        return
    msg = "Chatting " + message.value
    tools.smart_privmsg.send(bot, message, msg)
