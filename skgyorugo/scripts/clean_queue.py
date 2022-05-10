import sqlite3
import os
import ttv_api.users
import time
import logging

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")

STREAMER_PATH = os.path.abspath(os.path.join(__file__, "../.."))
streamer_login = os.path.split(STREAMER_PATH)[1]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)


def clean_queue():
    tries = 0
    while True:
        tries += 1
        twitch = ttv_api.users.get_users(user_logins=[streamer_login])
        if twitch:
            try:
                twitch_id = twitch[0].user_id
            except IndexError:
                logger.critical(
                    f"UNABLE TO CLEAN LOL QUEUE; GOT INDEX ERROR twitch = {twitch}"
                )
                continue
            break
        elif tries > 60:
            return
        logger.critical(f"UNABLE TO CLEAN LOL QUEUE; twitch = {twitch}")
        time.sleep(3)

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

    conn.close()
