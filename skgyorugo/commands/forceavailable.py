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

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Force user to become available in the list."
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
            "There was an issue fetching their twitch data. They weren't made unavailable.",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        UPDATE
            lol_queue
        SET
            position = (
                CASE
                    WHEN (
                        SELECT
                            position
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    ) < (
                        SELECT
                            max(position)
                        FROM
                            lol_queue
                        WHERE
                            available = 1
                        ORDER BY 
                            position
                        LIMIT (
                            SELECT
                                data
                            FROM
                                lol_queue_data
                            WHERE
                                name = 'queuesize'
                        )
                    )
                    THEN position + 1
                    ELSE position
                END
            )
        WHERE
            position > (
                SELECT
                    max(position)
                FROM
                    lol_queue
                WHERE
                    priority_queue = 1
                    OR position <= (
                        SELECT
                            max(position)
                        FROM
                            lol_queue
                        WHERE
                            available = 1
                        ORDER BY 
                            position
                        LIMIT (
                            SELECT
                                data
                            FROM
                                lol_queue_data
                            WHERE
                                name = 'queuesize'
                        )
                    )
            );
        """,
        (twitch_id,),
    )

    c.execute(
        """
        UPDATE
            lol_queue
        SET 
            available = 1,
            priority_queue = (
                CASE
                    WHEN (
                        SELECT
                            position
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    ) < (
                        SELECT
                            max(position)
                        FROM
                            lol_queue
                        WHERE
                            available = 1
                        ORDER BY 
                            position
                        LIMIT (
                            SELECT
                                data
                            FROM
                                lol_queue_data
                            WHERE
                                name = 'queuesize'
                        )
                    )
                    THEN 1
                    ELSE 0
                END
            ),
            position = 1 + (
                SELECT
                    max(position)
                FROM
                    lol_queue
                WHERE
                    priority_queue = 1
                    OR position <= (
                        SELECT
                            max(position)
                        FROM
                            lol_queue
                        WHERE
                            available = 1
                        ORDER BY 
                            position
                        LIMIT (
                            SELECT
                                data
                            FROM
                                lol_queue_data
                            WHERE
                                name = 'queuesize'
                        )
                    )
            )
            time_remaining = time_remaining - (? - last_available)
        WHERE 
            twitch_id = ?
            AND available = 0;
        """,
        (
            twitch_id,
            int(time.time()),
            twitch_id,
        ),
    )
    if c.rowcount < 1:
        bot.send_privmsg(
            message.channel,
            "They aren't in the list or they were already available.",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    c.execute("DELETE FROM lol_queue WHERE time_remaining < 0;")
    if c.rowcount > 0:
        bot.send_privmsg(
            message.channel,
            "They were unavailable for too long, they have been removed from the list.",
            reply=message.tags["id"],
        )
        conn.commit()
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully made them available",
        reply=message.tags["id"],
    )
    conn.close()
