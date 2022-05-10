from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r"Makes yourself temporarily unavailable in the list."
USER_COOLDOWN = 10
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch = ttv_api.users.get_users(user_logins=[message.nick])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching your twitch data. You weren't made unavailable.",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        UPDATE lol_queue SET available = 0, last_available = ? WHERE twitch_id = ?;
        """,
        (
            int(time.time()),
            twitch_id,
        ),
    )
    if not c.rowcount:
        bot.send_privmsg(
            message.channel,
            "You aren't in the list or you were already unavailable.",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully made you unavailable",
        reply=message.tags["id"],
    )
    conn.close()
