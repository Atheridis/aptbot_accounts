import os
import sqlite3

TOOLS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(TOOLS_PATH, "..")

DEFAULT_PERMISSION = 99


def get_permission_from_id(user_id: str) -> int:
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    c.execute("SELECT permission FROM users WHERE user_id = ?", (user_id,))
    fetched_user = c.fetchone()
    if fetched_user:
        return fetched_user[0]

    return DEFAULT_PERMISSION
