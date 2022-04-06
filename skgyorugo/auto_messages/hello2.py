from aptbot.bot import Message, Commands, Bot

COOLDOWN = 21 * 60
END_TIME = 2 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "MurphyAI reporting for duty!"
    bot.send_privmsg(message.channel, msg)
