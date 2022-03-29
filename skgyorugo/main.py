import tools.raid
import tools.smart_privmsg
import tools.permissions
from aptbot.bot import Bot, Message, Commands
import os
import importlib
import importlib.util
import sqlite3
from importlib import reload
import traceback
import ttv_api.users
import analyze_command

reload(tools.raid)
reload(tools.smart_privmsg)
reload(tools.permissions)

PATH = os.path.dirname(os.path.realpath(__file__))
COMMANDS_PATH = os.path.join(PATH, "commands")


commands = [
    c for c in os.listdir(COMMANDS_PATH) if os.path.isfile(os.path.join(COMMANDS_PATH, c))
]
commands = filter(lambda x: not x.startswith('.'), commands)
commands = filter(lambda x: os.path.splitext(x)[1] == ".py", commands)
commands = list(commands)
specs = {}
for command in commands:
    specs[command.split('.')[0]] = (
        importlib.util.spec_from_file_location(
            f"{command.split('.')[0]}",
            os.path.join(COMMANDS_PATH, command)
        )
    )

modules = {}
for command in specs:
    modules[command] = importlib.util.module_from_spec(specs[command])
    if not specs[command]:
        continue
    try:
        specs[command].loader.exec_module(modules[command])
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"Problem Loading Module: {e}")


def create_database():
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE commands (
            command TEXT NOT NULL,
            prefix TEXT NOT NULL,
            permission INTEGER NOT NULL,
            description TEXT,
            user_cooldown INTEGER NOT NULL,
            global_cooldown INTEGER NOT NULL,
            last_used INTEGER NOT NULL,
            PRIMARY KEY (command)
        )""")
    except sqlite3.OperationalError:
        print("Table commands exists")

    try:
        c.execute("""CREATE TABLE users (
            user_id text NOT NULL,
            permission INTEGER NOT NULL,
            PRIMARY KEY (user_id)
        )""")
    except sqlite3.OperationalError as e:
        print(f"Table users exists: {e}")
    else:
        aptbot_id = ttv_api.users.get_users(user_logins=["skgyorugo"])
        if aptbot_id:
            c.execute("INSERT INTO users VALUES (?, ?)",
                      (aptbot_id[0].user_id, 0))

    try:
        c.execute("""CREATE TABLE cooldowns (
            user_id TEXT NOT NULL,
            command TEXT NOT NULL,
            user_cooldown INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
            FOREIGN KEY(command) REFERENCES commands(command)
            PRIMARY KEY (user_id, command)
        )""")
    except sqlite3.OperationalError:
        print("Table cooldowns exists")

    try:
        c.execute("""CREATE TABLE command_values (
            command TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(command) REFERENCES commands(command)
        )""")
    except sqlite3.OperationalError:
        print("Table cooldowns exists")

    conn.commit()
    conn.close()


def update_commands_in_database():
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
        # try:
        c.execute(
            "REPLACE INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                command_name,
                command_prefix,
                command_permission,
                command_description,
                command_user_cooldown,
                command_global_cooldown,
                0,
            )
        )
    conn.commit()
    conn.close()


create_database()
update_commands_in_database()


def main(bot: Bot, message: Message):
    if message.command == Commands.PRIVMSG:
        analyze_command.do_command(bot, message, modules)

    tools.raid.raid(bot, message)
