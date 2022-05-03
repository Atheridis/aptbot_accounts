import time
import os
import ttv_api.users
import ttv_api.stream
import ttv_api.channel
import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

STREAMER_PATH = os.path.abspath(os.path.join(__file__, "../.."))
logger.debug(f"STREAMER_PATH set to: {STREAMER_PATH}")
TOOLS_PATH = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"TOOLS_PATH set to: {TOOLS_PATH}")
PATH = os.path.join(TOOLS_PATH, "..")
logger.debug(f"PATH set to: {PATH}")


CHECK_STREAMTIME_CD = 5 * 60
MAX_OFF_STREAM_MARGIN = 60 * 60


def start_stream_timestamp() -> Optional[int]:
    streamer_login = os.path.split(STREAMER_PATH)[1]
    logger.debug(f"streamer_login set to: {streamer_login}")

    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    c.execute("SELECT MAX(last_checked) FROM stream_info")
    max_last_checked = c.fetchone()
    if max_last_checked:
        c.execute(
            """
            SELECT
                start_stream_ts,
                last_checked
            FROM
                stream_info
            WHERE
                last_checked = ?
                AND ended = 0
            """,
            (
                max_last_checked[0],
            )
        )

    fetched = c.fetchone()

    if fetched:
        start_stream_ts, last_checked = fetched
        logger.debug(f"start_stream_ts set to: {start_stream_ts}")
        logger.debug(f"last_checked set to: {last_checked}")
        if time.time() < last_checked + CHECK_STREAMTIME_CD:
            logger.info(f"returned cached start stream time: {start_stream_ts}")
            conn.close()
            return start_stream_ts

    stream_info = ttv_api.stream.get_streams(user_logins=[streamer_login])
    logger.info(f"used twitch api to get stream info")
    if not stream_info and not fetched:
        logger.info(f"streamer {streamer_login} is currently not streaming")
        conn.close()
        return

    if not stream_info:
        start_stream_ts, last_checked = fetched
        logger.debug(f"start_stream_ts set to: {start_stream_ts}")
        logger.debug(f"last_checked set to: {last_checked}")
        if time.time() < last_checked + MAX_OFF_STREAM_MARGIN:
            logger.info(f"streamer {streamer_login} is currently not streaming, stream not considered ended yet")
            conn.close()
            return

        c.execute(
            "REPLACE INTO stream_info VALUES (?, ?, ?)",
            (
                start_stream_ts,
                last_checked,
                1,
            )
        )
        conn.commit()
        logger.info(f"streamer {streamer_login} has ended stream")
        conn.close()
        return

    if not fetched:
        start_stream_ts = int(stream_info[0].started_at.timestamp())
        current_time = int(time.time())
        c.execute(
            "REPLACE INTO stream_info VALUES (?, ?, ?)",
            (
                start_stream_ts,
                current_time,
                0,
            )
        )
        conn.commit()
        logger.info(f"inserted database with start stream {start_stream_ts}, last updated {current_time}")
        conn.close()
        logger.info(f"returned api start stream time: {start_stream_ts}")
        return start_stream_ts

    start_stream_ts, last_checked = fetched
    current_time = int(time.time())
    c.execute(
        "REPLACE INTO stream_info VALUES (?, ?, ?)",
        (
            start_stream_ts,
            current_time,
            0,
        )
    )
    conn.commit()
    logger.info(f"updated database with cached start stream {start_stream_ts}, last updated {current_time}")
    conn.close()
    logger.info(f"returned cached start stream time: {start_stream_ts}")
    return start_stream_ts
