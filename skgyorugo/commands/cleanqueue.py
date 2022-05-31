from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import time

logger = logging.getLogger(__name__)

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Cleans the whole queue"
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch = ttv_api.users.get_users(user_logins=[message.channel])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            f"There was an issue fetching {message.channel} twitch data. The queue was not cleared.",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id

    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute("DELETE FROM lol_queue")
    conn.commit()

    c.execute(
        """
        INSERT INTO lol_queue (
            "twitch_id",
            "position",
            "available",
            "last_available",
            "time_remaining"
        ) VALUES (?, ?, ?, ?, ?);
        """,
        (
            twitch_id,
            0,
            1,
            None,
            9999999,
        ),
    )
    conn.commit()

    bot.send_privmsg(
        message.channel,
        f"Successfully cleaned the queue.",
        reply=message.tags["id"],
    )

    conn.close()
