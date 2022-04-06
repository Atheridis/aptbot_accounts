import sqlite3
import os
import ttv_api.users

PATH = os.path.dirname(os.path.realpath(__file__))

STREAMER_PATH = os.path.abspath(os.path.join(__file__, ".."))
streamer_login = os.path.split(STREAMER_PATH)[1]


def create_variables_db():
    conn = sqlite3.connect(os.path.join(PATH, "variables.db"))
    c = conn.cursor()

    try:
        c.execute(
            """
            CREATE TABLE variables (
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (name)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE methods (
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                input TEXT,
                PRIMARY KEY (name, type)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE list_values (
                id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY(name) REFERENCES variables(name)
                PRIMARY KEY (id, name)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    conn.close()


def create_database():
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    try:
        c.execute(
            """
            CREATE TABLE commands (
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
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE users (
                user_id text NOT NULL,
                permission INTEGER NOT NULL,
                PRIMARY KEY (user_id)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    admin_id = ttv_api.users.get_users(user_logins=["skgyorugo"])
    broadcaster_id = ttv_api.users.get_users(user_logins=[streamer_login])
    if admin_id:
        try:
            c.execute("INSERT INTO users VALUES (?, ?)",
                      (admin_id[0].user_id, 0))
        except sqlite3.IntegrityError as e:
            print(e)
    if broadcaster_id:
        try:
            c.execute("INSERT INTO users VALUES (?, ?)",
                      (broadcaster_id[0].user_id, 1))
        except sqlite3.IntegrityError as e:
            print(e)

    try:
        c.execute(
            """
            CREATE TABLE cooldowns (
                user_id TEXT NOT NULL,
                command TEXT NOT NULL,
                user_cooldown INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
                FOREIGN KEY(command) REFERENCES commands(command)
                PRIMARY KEY (user_id, command)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE command_values (
                command TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY(command) REFERENCES commands(command)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE auto_messages (
                name TEXT NOT NULL,
                cooldown INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                last_used INTEGER NOT NULL,
                PRIMARY KEY (name)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE auto_message_values (
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY(name) REFERENCES auto_messages(name)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    try:
        c.execute(
            """
            CREATE TABLE stream_info (
                start_stream_ts INTEGER NOT NULL,
                last_checked INTEGER NOT NULL,
                ended INTEGER NOT NULL,
                PRIMARY KEY (start_stream_ts)
            )
            """
        )
    except sqlite3.OperationalError as e:
        print(e)

    conn.commit()
    conn.close()


def update_commands_in_database(modules, commands):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    for command in commands:
        command_name = command.split('.')[0]
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
            )
        )
    conn.commit()
    conn.close()


def update_auto_messages_in_database(modules, auto_messages):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    for auto_message in auto_messages:
        auto_message_name = auto_message.split('.')[0]
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
                )
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
                )
            )
    conn.commit()
    conn.close()
