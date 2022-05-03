from aptbot.bot import Bot, Message, Commands
import os
import sqlite3
import time
import tools.smart_privmsg
import tools.smart_start_stream_time
import logging
from importlib import reload

reload(tools.smart_privmsg)
reload(tools.smart_start_stream_time)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

PATH = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"analyze_auto_message PATH set to: {PATH}")


def do_auto_message(bot: Bot, message: Message, auto_message_modules: dict):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    start_stream_ts = tools.smart_start_stream_time.start_stream_timestamp()
    if not start_stream_ts:
        return

    c.execute(
        """
        SELECT
            name,
            cooldown,
            end_time,
            last_used,
            value
        FROM
            auto_messages
        LEFT JOIN auto_message_values USING (name)
        ORDER BY
            last_used ASC
        """
    )
    while True:
        fetched = c.fetchone()
        if not fetched:
            break

        name, cooldown, end_time, last_used, value = fetched
        if time.time() < last_used + cooldown:
            continue
        if time.time() > start_stream_ts + end_time and end_time != 0:
            continue
        if value:
            tools.smart_privmsg.send(bot, message, value)
        else:
            try:
                auto_message_modules[name].main(bot, message)
            except KeyError:
                c.execute(
                    """
                        DELETE FROM
                            auto_messages
                        WHERE
                            name = ?
                    """,
                    (name, )
                )
                conn.commit()
                continue

        c.execute(
            "UPDATE auto_messages SET last_used = ? WHERE name = ?",
            (
                int(time.time()),
                name,
            )
        )
        conn.commit()
        break
    conn.close()
