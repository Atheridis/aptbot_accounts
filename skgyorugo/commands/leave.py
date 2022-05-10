from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = (
    r"Leaves the queue which gives you the privalege to play with the streamer."
)
USER_COOLDOWN = 60
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch = ttv_api.users.get_users(user_logins=[message.nick])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching your twitch data. You weren't removed from the list Sadge",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        DELETE FROM lol_queue WHERE twitch_id = ?;
        """,
        (twitch_id,),
    )
    if not c.rowcount:
        bot.send_privmsg(
            message.channel,
            "You weren't in the list.",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully removed you from the list",
        reply=message.tags["id"],
    )
    conn.close()
