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

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Move the user down one row in the queue."
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch_name = message.tags.get("reply-parent-user-login", None)
    if not twitch_name:
        twitch_name = message.value.split(" ")[1]
    twitch = ttv_api.users.get_users(user_logins=[twitch_name])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching the user's twitch data. They weren't moved down in the list Sadge",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id

    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE
                lol_queue
            SET
                position = (
                    SELECT
                        min(position)
                    FROM
                        lol_queue
                    WHERE
                        position > (
                            SELECT
                                position
                            FROM
                                lol_queue
                            WHERE
                                twitch_id = ?
                        )
                ) + (
                    SELECT
                        position
                    FROM
                        lol_queue
                    WHERE
                        twitch_id = ?
                ) - position
            WHERE
                position in (
                    (
                        SELECT
                            min(position)
                        FROM
                            lol_queue
                        WHERE
                            position > (
                                SELECT
                                    position
                                FROM
                                    lol_queue
                                WHERE
                                    twitch_id = ?
                            )
                    ),
                    (
                        SELECT
                            position 
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    )
                );
            """,
            (twitch_id,) * 4,
        )
    except sqlite3.IntegrityError:
        bot.send_privmsg(
            message.channel, "Can't move user down further", reply=message.tags["id"]
        )
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel, "Successfully moved them down.", reply=message.tags["id"]
    )
    conn.close()
