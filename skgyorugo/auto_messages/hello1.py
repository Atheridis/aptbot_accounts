from aptbot.bot import Message, Commands, Bot

COOLDOWN = 7 * 60
END_TIME = 0.5 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "peepoWave"
    bot.send_privmsg(message.channel, msg)

