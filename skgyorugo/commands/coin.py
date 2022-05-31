from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import random

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = (
    r"Tosses a coin, there's a 50% chance it's heads and a 50% chance it's tails"
)
USER_COOLDOWN = 10
GLOBAL_COOLDOWN = 5


def main(bot: Bot, message: Message):
    r = random.random()
    if r < 0.02:
        tools.smart_privmsg.send(
            bot,
            message,
            f"the coin landed on it's side, try again.",
            reply=message.tags["id"],
        )
    elif r < 0.51:
        tools.smart_privmsg.send(bot, message, f"heads", reply=message.tags["id"])
    else:
        tools.smart_privmsg.send(bot, message, f"tails", reply=message.tags["id"])
