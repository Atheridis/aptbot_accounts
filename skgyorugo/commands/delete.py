from aptbot.bot import Message, Commands, Bot

PERMISSION = 10
PREFIX = '\\'
DESCRIPTION = "Reply to a message with \\delete to delete that message"
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

def main(bot: Bot, message: Message):
    try:
        replied_msg_id = message.tags["reply-parent-msg-id"]
    except KeyError:
        return
    delete = f"/delete {replied_msg_id}"
    bot.send_privmsg(message.channel, delete)

