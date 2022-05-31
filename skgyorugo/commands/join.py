from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3

logger = logging.getLogger(__name__)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r"Joins the queue to play the game with the streamer."
USER_COOLDOWN = 60
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")

DEFAULT_TIME_REMAINING = 60 * 60


def main(bot: Bot, message: Message):
    twitch = ttv_api.users.get_users(user_logins=[message.nick])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching your twitch data. You weren't added to the list Sadge",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        SELECT position FROM lol_queue ORDER BY position DESC;
        """
    )

    try:
        last_position: int = c.fetchone()[0]
    except TypeError:
        last_position: int = -1

    try:
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
                last_position + 1,
                1,
                None,
                DEFAULT_TIME_REMAINING,
            ),
        )
    except sqlite3.IntegrityError:
        bot.send_privmsg(
            message.channel,
            "You are already added into the list",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully added you into the list",
        reply=message.tags["id"],
    )
    conn.close()
