import time
import os
import ttv_api.users
import ttv_api.stream
import ttv_api.channel
import sqlite3
import logging
from scripts import clean_queue
from typing import Optional

logger = logging.getLogger(__name__)

STREAMER_PATH = os.path.abspath(os.path.join(__file__, "../.."))
logger.debug(f"STREAMER_PATH set to: {STREAMER_PATH}")
TOOLS_PATH = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"TOOLS_PATH set to: {TOOLS_PATH}")
PATH = os.path.join(TOOLS_PATH, "..")
logger.debug(f"PATH set to: {PATH}")

STREAMER_LOGIN = os.path.split(STREAMER_PATH)[1]
logger.debug(f"streamer_login set to: {STREAMER_LOGIN}")


CHECK_STREAMTIME_CD = 5 * 60
MAX_OFF_STREAM_MARGIN = 60 * 60


def end_stream():
    logger.info(f"{STREAMER_LOGIN} has ended their stream")
    clean_queue.clean_queue()


def start_stream():
    logger.info(f"{STREAMER_LOGIN} has started their stream")
    clean_queue.clean_queue()


def start_stream_timestamp() -> Optional[int]:
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    c.execute(
        """
        SELECT
            start_stream_ts
        FROM
            stream_info
        WHERE
            ended = 0;
        """
    )

    fetched = c.fetchone()
    conn.close()

    try:
        return fetched[0]
    except TypeError:
        return None


def update_start_stream_timestamp() -> Optional[str]:
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
            (max_last_checked[0],),
        )

    fetched = c.fetchone()

    if fetched:
        start_stream_ts, last_checked = fetched
        if time.time() < last_checked + CHECK_STREAMTIME_CD:
            conn.close()
            return

    stream_info = ttv_api.stream.get_streams(user_logins=[STREAMER_LOGIN])
    if not stream_info and not fetched:
        conn.close()
        return

    if not stream_info:
        start_stream_ts, last_checked = fetched
        if time.time() < last_checked + MAX_OFF_STREAM_MARGIN:
            conn.close()
            return

        c.execute(
            "REPLACE INTO stream_info VALUES (?, ?, ?)",
            (
                start_stream_ts,
                last_checked,
                1,
            ),
        )
        conn.commit()
        conn.close()
        # TODO add hook, streamer ended stream
        end_stream()
        return "END"

    if not fetched:
        start_stream_ts = int(stream_info[0].started_at.timestamp())
        current_time = int(time.time())
        c.execute(
            "REPLACE INTO stream_info VALUES (?, ?, ?)",
            (
                start_stream_ts,
                current_time,
                0,
            ),
        )
        conn.commit()
        conn.close()
        start_stream()
        return "START"

    start_stream_ts, last_checked = fetched
    current_time = int(time.time())
    c.execute(
        "REPLACE INTO stream_info VALUES (?, ?, ?)",
        (
            start_stream_ts,
            current_time,
            0,
        ),
    )
    conn.commit()
    conn.close()
    return
