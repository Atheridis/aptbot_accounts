import time
import os
import ttv_api.users
import ttv_api.stream
import ttv_api.channel
import sqlite3
from typing import Optional

STREAMER_PATH = os.path.abspath(os.path.join(__file__, "../.."))
TOOLS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(TOOLS_PATH, "..")


CHECK_STREAMTIME_CD = 5 * 60
MAX_OFF_STREAM_MARGIN = 60 * 60


def start_stream_timestamp() -> Optional[int]:
    streamer_login = os.path.split(STREAMER_PATH)[1]

    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    c.execute("SELECT MAX(last_checked) FROM stream_info")
    max_last_checked = c.fetchone()
    if max_last_checked:
        c.execute(
            """
            SELECT
                start_stream_ts,
                last_checked,
                ended
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
        print(f"I checked {max_last_checked}")

    fetched = c.fetchone()
    if fetched:
        start_stream_ts, last_checked, _ = fetched
        print(f"stream ts = {start_stream_ts}")
        print(
            f"last_checked {last_checked} + check_streamtime_cd {CHECK_STREAMTIME_CD} \n time.time {time.time()}")
        if time.time() < last_checked + CHECK_STREAMTIME_CD:
            return start_stream_ts

    stream_info = ttv_api.stream.get_streams(user_logins=[streamer_login])
    if not stream_info and not fetched:
        return

    if not stream_info:
        start_stream_ts, last_checked, _ = fetched
        if time.time() < last_checked + MAX_OFF_STREAM_MARGIN:
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
        conn.close()
        return

    if not fetched:
        start_stream_ts = int(stream_info[0].started_at.timestamp())
        print("TEST")
        c.execute(
            "REPLACE INTO stream_info VALUES (?, ?, ?)",
            (
                start_stream_ts,
                int(time.time()),
                0,
            )
        )
        conn.commit()
        conn.close()
        return start_stream_ts

    print("MORE TEST")
    start_stream_ts, last_checked, _ = fetched
    c.execute(
        "REPLACE INTO stream_info VALUES (?, ?, ?)",
        (
            start_stream_ts,
            int(time.time()),
            0,
        )
    )
    conn.commit()
    conn.close()
    return start_stream_ts
