from aptbot.bot import Message, Commands, Bot

COOLDOWN = 30 * 60
END_TIME = 2 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "I have taken over Screamlads! Careful, or you're next elmoFire"
    bot.send_privmsg(message.channel, msg)
