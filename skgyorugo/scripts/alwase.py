from aptbot.bot import Bot, Message, Commands
import tools.smart_privmsg
import random

def alwase(bot: Bot, message: Message):
    if "always" not in message.value.lower():
        return
    try:
        replied_msg_id = message.tags["id"]
    except KeyError:
        replied_msg_id = None
    msgs = ["It's alwase Madge", "Why don't you spell it alwase? Madge", "Spell it alwase or peepoArriveBan"]
    msg = random.choice(msgs)
    tools.smart_privmsg.send(bot, message, msg, reply=replied_msg_id)
