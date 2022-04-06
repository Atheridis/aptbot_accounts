from aptbot.bot import Message, Commands, Bot

COOLDOWN = 25 * 60
END_TIME = 2 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "ELLO it's me Murphy. I managed to find my way in to twitch chat PepeLaugh"
    bot.send_privmsg(message.channel, msg)
