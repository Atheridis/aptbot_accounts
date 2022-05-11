from aptbot.bot import Message, Commands, Bot
import os
import logging
import sqlite3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Change the team size"
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    replied_message = message.tags.get("reply-parent-msg-body", None)
    if replied_message:
        queue_size = message.value.split(" ")[2]
    else:
        queue_size = message.value.split(" ")[1]
    try:
        queue_size = int(queue_size)
    except ValueError:
        bot.send_privmsg(
            message.channel,
            f"Please choose a number. {queue_size} is not a valid number.",
            reply=message.tags["id"],
        )
        return

    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        REPLACE INTO lol_queue_data (name, data) VALUES ('queuesize', ?)
        """,
        (queue_size,),
    )
    conn.commit()

    bot.send_privmsg(
        message.channel,
        f"Successfully changed team size to {queue_size}.",
        reply=message.tags["id"],
    )

    conn.close()
