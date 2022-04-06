from aptbot.bot import Bot, Message, Commands
import os
import sqlite3
import time
import tools.smart_privmsg
import tools.smart_start_stream_time
from importlib import reload

reload(tools.smart_privmsg)
reload(tools.smart_start_stream_time)

PATH = os.path.dirname(os.path.realpath(__file__))


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
        """
    )
    fetched = c.fetchall()
    if not fetched:
        conn.close()
        return

    for auto_message in fetched:
        name, cooldown, end_time, last_used, value = auto_message
        print(auto_message)
        if time.time() < last_used + cooldown:
            continue
        if time.time() > start_stream_ts + end_time and end_time != 0:
            continue
        if value:
            tools.smart_privmsg.send(bot, message, value)
        else:
            auto_message_modules[name].main(bot, message)
        c.execute(
            "REPLACE INTO auto_messages VALUES (?, ?, ?, ?)",
            (
                name,
                cooldown,
                end_time,
                int(time.time()),
            )
        )
        conn.commit()
        time.sleep(1.5)
    conn.close()
