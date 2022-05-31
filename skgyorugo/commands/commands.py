from aptbot.bot import Message, Commands, Bot
import tools.permissions
import tools.smart_privmsg
import sqlite3
import os

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = ""
USER_COOLDOWN = 30
GLOBAL_COOLDOWN = 15


COMMANDS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(COMMANDS_PATH, "..")


def main(bot: Bot, message: Message):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

    user_perm = tools.permissions.get_permission_from_id(message.tags["user-id"])

    c.execute(
        "SELECT prefix, command FROM commands WHERE permission >= ? ORDER BY permission ASC",
        (user_perm,),
    )

    fetched_commands = c.fetchall()

    conn.commit()
    conn.close()

    commands = []
    for command in fetched_commands:
        commands.append(f"{command[0]}{command[1]}")

    commands = " ".join(commands)
    tools.smart_privmsg.send(bot, message, commands)
