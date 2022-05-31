from aptbot.bot import Message, Commands, Bot
import sqlite3
import os

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0


COMMANDS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(COMMANDS_PATH, "..")


def main(bot: Bot, message: Message):
    msg = " ".join(message.value.split(" ")[1:])
    command = msg.split(" ")[0]
    command_prefix = command[0]
    command_name = command[1:]
    command_value = msg = " ".join(msg.split(" ")[1:])
    if command_prefix != "?":
        bot.send_privmsg(
            message.channel,
            f"{message.nick} you cannot use {command_prefix} as a prefix",
        )
        return

    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    c.execute(
        "SELECT value FROM commands LEFT JOIN command_values USING(command) WHERE command = ? AND prefix = ?",
        (
            command_name,
            command_prefix,
        ),
    )
    if not c.fetchone()[0]:
        bot.send_privmsg(
            message.channel,
            f"The command {command_prefix}{command_name} cannot be edited",
        )
        return

    try:
        c.execute(
            "UPDATE command_values SET value = ? WHERE command = ?",
            (
                command_value,
                command_name,
            ),
        )
    except sqlite3.IntegrityError:
        bot.send_privmsg(message.channel, f"The command {command_name} doesn't exist.")
    else:
        bot.send_privmsg(message.channel, f"Successfully updated {command_name}.")
    conn.commit()
    conn.close()
