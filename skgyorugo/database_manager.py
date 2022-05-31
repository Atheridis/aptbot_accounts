from aptbot.bot import Message, Commands
import sqlite3
import os
import ttv_api.users
import logging

logger = logging.getLogger(__name__)

PATH = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"PATH set to: {PATH}")

STREAMER_PATH = os.path.abspath(os.path.join(__file__, ".."))
logger.debug(f"STREAMER_PATH set to: {STREAMER_PATH}")
streamer_login = os.path.split(STREAMER_PATH)[1]
logger.debug(f"streamer_login set to: {streamer_login}")


def create_variables_db():
    db_name_var = "variables.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_var))
    c = conn.cursor()
    logger.info(f"connected to database {db_name_var}")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS variables (
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (name)
        )
        """
    )
    logger.info(f"created table variables")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS methods (
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            input TEXT,
            PRIMARY KEY (name, type)
        )
        """
    )
    logger.info(f"created table methods")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS list_values (
            id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(name) REFERENCES variables(name)
            PRIMARY KEY (id, name)
        )
        """
    )
    logger.info(f"created table list_values")

    conn.commit()
    conn.close()


def create_lol_database():
    db_name_database = "lol_data.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_database))
    c = conn.cursor()
    logger.info(f"connected to database {db_name_database}")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            puuid TEXT NOT NULL,
            summoner_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            twitch_id INTEGER,
            PRIMARY KEY (puuid)
        )
        """
    )
    logger.info(f"created table accounts")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS lol_queue (
            twitch_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            available INTEGER NOT NULL,
            last_available INTEGER,
            time_remaining INTEGER NOT NULL,
            team INTEGER,
            priority_queue INTEGER,
            PRIMARY KEY (twitch_id)
        );
        """
    )
    logger.info(f"created table lol_queue")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS lol_queue_data (
            name TEXT NOT NULL,
            data INTEGER NOT NULL,
            PRIMARY KEY (name)
        );
        """
    )
    logger.info(f"created table lol_queue_data")

    conn.commit()
    conn.close()


def create_database():
    db_name_database = "database.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_database))
    c = conn.cursor()
    logger.info(f"connected to database {db_name_database}")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            command TEXT NOT NULL,
            prefix TEXT NOT NULL,
            permission INTEGER NOT NULL,
            description TEXT,
            user_cooldown INTEGER NOT NULL,
            global_cooldown INTEGER NOT NULL,
            last_used INTEGER NOT NULL,
            PRIMARY KEY (command)
        )
        """
    )
    logger.info(f"created table commands")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id text NOT NULL,
            permission INTEGER NOT NULL,
            PRIMARY KEY (user_id)
        )
        """
    )
    logger.info(f"created table users")

    admin_id = ttv_api.users.get_users(user_logins=["skgyorugo"])
    aptbot_id = ttv_api.users.get_users(user_logins=["murphyai"])
    broadcaster_id = ttv_api.users.get_users(user_logins=[streamer_login])
    if admin_id:
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (admin_id[0].user_id, 0))
        logger.info(f"inserted user {admin_id[0].user_id} with permission {0}")
    if aptbot_id:
        c.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?)", (aptbot_id[0].user_id, 0)
        )
        logger.info(f"inserted user {aptbot_id[0].user_id} with permission {0}")
    if broadcaster_id:
        c.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?)", (broadcaster_id[0].user_id, 1)
        )
        logger.info(f"inserted user {broadcaster_id[0].user_id} with permission {1}")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id TEXT NOT NULL,
            command TEXT NOT NULL,
            user_cooldown INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
            FOREIGN KEY(command) REFERENCES commands(command)
            PRIMARY KEY (user_id, command)
        )
        """
    )
    logger.info(f"created table cooldowns")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS command_values (
            command TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(command) REFERENCES commands(command)
        )
        """
    )
    logger.info(f"created table command_values")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS auto_messages (
            name TEXT NOT NULL,
            cooldown INTEGER NOT NULL,
            end_time INTEGER NOT NULL,
            last_used INTEGER NOT NULL,
            PRIMARY KEY (name)
        )
        """
    )
    logger.info(f"created table auto_messages")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS auto_message_values (
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(name) REFERENCES auto_messages(name)
        )
        """
    )
    logger.info(f"created table auto_message_values")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS stream_info (
            start_stream_ts INTEGER NOT NULL,
            last_checked INTEGER NOT NULL,
            ended INTEGER NOT NULL,
            PRIMARY KEY (start_stream_ts)
        )
        """
    )
    logger.info(f"created table stream_info")

    conn.commit()
    conn.close()


def update_commands_in_database(modules, commands):
    db_name_database = "database.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_database))
    c = conn.cursor()
    logger.info(f"connected to database {db_name_database}")

    for command in commands:
        command_name = command.split(".")[0]
        command_permission = modules[command_name].PERMISSION
        command_prefix = modules[command_name].PREFIX
        command_description = modules[command_name].DESCRIPTION
        command_user_cooldown = modules[command_name].USER_COOLDOWN
        command_global_cooldown = modules[command_name].GLOBAL_COOLDOWN
        command_last_used = 0
        c.execute(
            "REPLACE INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                command_name,
                command_prefix,
                command_permission,
                command_description,
                command_user_cooldown,
                command_global_cooldown,
                command_last_used,
            ),
        )
        logger.info(f"updating commands command_name: {command_name}")
        logger.debug(f"updating commands command_prefix: {command_prefix}")
        logger.debug(f"updating commands command_permission: {command_permission}")
        logger.debug(f"updating commands command_description: {command_description}")
        logger.debug(
            f"updating commands command_user_cooldown: {command_user_cooldown}"
        )
        logger.debug(
            f"updating commands command_global_cooldown: {command_global_cooldown}"
        )
        logger.debug(f"updating commands command_last_used: {command_last_used}")
    conn.commit()
    conn.close()


def add_message_to_chat_history(message: Message):
    if message.command != Commands.PRIVMSG:
        return
    conn = sqlite3.connect(os.path.join(PATH, "chat_history.db"))
    c = conn.cursor()

    try:
        bits = message.tags["bits"]
    except KeyError:
        bits = None
    try:
        rp_display_name = message.tags["reply-parent-display-name"]
        rp_msg_body = message.tags["reply-parent-msg-body"]
        rp_msg_id = message.tags["reply-parent-msg-id"]
        rp_user_id = int(message.tags["reply-parent-user-id"])
        rp_user_login = message.tags["reply-parent-user-login"]
    except KeyError:
        rp_display_name = None
        rp_msg_body = None
        rp_msg_id = None
        rp_user_id = None
        rp_user_login = None

    c.execute(
        """
        INSERT INTO chat (
            "id",
            "nick",
            "channel",
            "message",
            "tmi-sent-ts",
            "badge-info",
            "badges",
            "bits",
            "color",
            "display-name",
            "first-msg",
            "mod",
            "room-id",
            "user-id",
            "user-type",
            "turbo",
            "subscriber",
            "reply-parent-display-name",
            "reply-parent-msg-body",
            "reply-parent-msg-id",
            "reply-parent-user-id",
            "reply-parent-user-login"
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
        """,
        (
            message.tags["id"],
            message.nick,
            message.channel,
            message.value,
            int(message.tags["tmi-sent-ts"]),
            message.tags["badge-info"],
            message.tags["badges"],
            bits,
            message.tags["color"],
            message.tags["display-name"],
            int(message.tags["first-msg"]),
            int(message.tags["mod"]),
            int(message.tags["room-id"]),
            int(message.tags["user-id"]),
            message.tags["user-type"],
            int(message.tags["turbo"]),
            int(message.tags["subscriber"]),
            rp_display_name,
            rp_msg_body,
            rp_msg_id,
            rp_user_id,
            rp_user_login,
        ),
    )
    conn.commit()
    conn.close()


def create_chat_history_database():
    conn = sqlite3.connect(os.path.join(PATH, "chat_history.db"))
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS "chat" (
            "id"	TEXT NOT NULL,
            "nick"	TEXT NOT NULL,
            "channel"	TEXT NOT NULL,
            "message"	TEXT NOT NULL,
            "tmi-sent-ts"	INTEGER NOT NULL,
            "badge-info"	TEXT NOT NULL,
            "badges"	TEXT NOT NULL,
            "bits"	TEXT,
            "color"	TEXT NOT NULL,
            "display-name"	TEXT NOT NULL,
            "first-msg"	INTEGER NOT NULL,
            "mod"	INTEGER NOT NULL,
            "room-id"	INTEGER NOT NULL,
            "user-id"	INTEGER NOT NULL,
            "user-type"	TEXT NOT NULL,
            "turbo"	INTEGER NOT NULL,
            "subscriber"	INTEGER NOT NULL,
            "reply-parent-display-name"	TEXT,
            "reply-parent-msg-body"	TEXT,
            "reply-parent-msg-id"	TEXT,
            "reply-parent-user-id"	INTEGER,
            "reply-parent-user-login"	TEXT,
            PRIMARY KEY("id")
        );
        """
    )
    conn.commit()
    conn.close()


def update_auto_messages_in_database(modules, auto_messages):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    for auto_message in auto_messages:
        auto_message_name = auto_message.split(".")[0]
        auto_message_cooldown = modules[auto_message_name].COOLDOWN
        auto_message_end_time = modules[auto_message_name].END_TIME
        auto_message_last_used = 0
        try:
            c.execute(
                "INSERT INTO auto_messages (name, cooldown, end_time, last_used) VALUES (?, ?, ?, ?)",
                (
                    auto_message_name,
                    auto_message_cooldown,
                    auto_message_end_time,
                    auto_message_last_used,
                ),
            )
        except Exception as e:
            c.execute(
                """
                UPDATE auto_messages
                SET
                    cooldown = ?,
                    end_time = ?
                WHERE
                    name = ?
                """,
                (
                    auto_message_cooldown,
                    auto_message_end_time,
                    auto_message_name,
                ),
            )
    conn.commit()
    conn.close()
