from aptbot.bot import Message, Commands, Bot

COOLDOWN = 8 * 60
END_TIME = 2 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "IF YOU WANT TO PLAY WITH PEKS TYPE: ?join ------------------------------------------------------------------------------- You can find more info here: https://i.imgur.com/hqW5OOn.png"
    bot.send_privmsg(message.channel, msg)
