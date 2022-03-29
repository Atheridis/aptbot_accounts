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

reload(tools.raid)
reload(tools.smart_privmsg)
reload(tools.permissions)

PATH = os.path.dirname(os.path.realpath(__file__))
COMMANDS_PATH = os.path.join(PATH, "commands")


commands = [
    c for c in os.listdir(COMMANDS_PATH) if os.path.isfile(os.path.join(COMMANDS_PATH, c))
]
specs = {}
for command in commands:
    if not command.split('.')[0]:
        continue
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
            command text PRIMARY KEY,
            prefix text,
            permission integer,
            value text,
            description text,
            user_cooldown int,
            global_cooldown int
        )""")
    except sqlite3.OperationalError:
        print("Table commands exists")

    try:
        c.execute("""CREATE TABLE users (
            user_id text PRIMARY KEY,
            permission integer
        )""")
    except sqlite3.OperationalError:
        print("Table users exists")
    else:
        aptbot_id = ttv_api.users.get_users(user_logins=["skgyorugo"])
        if aptbot_id:
            c.execute("INSERT INTO users VALUES (?, ?)",
                      (aptbot_id[0].user_id, 0))

    try:
        c.execute("""CREATE TABLE cooldowns (
            user_id text,
            command text,
            prefix text,
            user_cooldown integer,
            global_cooldown integer,
            PRIMARY KEY (user_id, command)
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
        # try:
        c.execute(
            "REPLACE INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                command_name,
                command_prefix,
                command_permission,
                None,
                command_description,
                command_user_cooldown,
                command_global_cooldown,
            )
        )
    conn.commit()
    conn.close()


create_database()
update_commands_in_database()


def main(bot: Bot, message: Message):
    if message.command == Commands.PRIVMSG:
        conn = sqlite3.connect(os.path.join(PATH, "database.db"))
        c = conn.cursor()
        command = message.value.split(' ')[0]
        prefix = command[0]
        command = command[1:]
        c.execute("SELECT * FROM commands WHERE command = ?", (command,))
        fetched_command = c.fetchone()
        user_perm = tools.permissions.get_permission_from_id(
            message.tags["user-id"]
        )
        message_timestamp = int(message.tags["tmi-sent-ts"]) // 1000
        if fetched_command and prefix == fetched_command[1] and user_perm <= fetched_command[2]:
            c.execute(
                "SELECT global_cooldown FROM cooldowns WHERE command = ? ORDER BY global_cooldown DESC",
                (command, )
            )
            try:
                fetched_global_cooldown = c.fetchone()[0]
            except TypeError:
                fetched_global_cooldown = 0
            c.execute(
                "SELECT user_cooldown FROM cooldowns WHERE user_id = ? AND command = ?",
                (message.tags["user-id"], command)
            )
            try:
                fetched_user_cooldown = c.fetchone()[0]
            except TypeError:
                fetched_user_cooldown = 0
            cooldown = max(fetched_global_cooldown, fetched_user_cooldown)
            if message_timestamp > cooldown:
                c.execute(
                    "SELECT user_cooldown, global_cooldown FROM commands WHERE command = ?",
                    (command, )
                )
                user_cooldown, global_cooldown = c.fetchone()
                c.execute(
                    "REPLACE INTO cooldowns VALUES (?, ?, ?, ?, ?)",
                    (
                        message.tags["user-id"],
                        command,
                        prefix,
                        user_cooldown + message_timestamp,
                        global_cooldown + message_timestamp,
                    )
                )
                conn.commit()
                if not fetched_command[3]:
                    modules[command].main(bot, message)
                elif fetched_command[3]:
                    tools.smart_privmsg.send(bot, message, fetched_command[3])
            else:
                bot.send_privmsg(
                    message.channel,
                    f"The command '{prefix}{command}' is on cooldown. \
                    Please wait {int(cooldown - message_timestamp) + 1} seconds."
                )

        conn.commit()
        conn.close()

    tools.raid.raid(bot, message)
