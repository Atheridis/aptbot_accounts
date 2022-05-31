from aptbot.bot import Message, Commands, Bot
import sqlite3
import os

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")

DEFAULT_PERMISSION = 99
DEFAULT_DESCRIPTION = ""
DEFAULT_USER_COOLDOWN = 5
DEFAULT_GLOBAL_COOLDOWN = 0
DEFAULT_LAST_USED = 0


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
    try:
        if not c.fetchone()[0]:
            bot.send_privmsg(
                message.channel,
                f"The command {command_prefix}{command_name} already exists",
            )
            return
    except TypeError:
        pass
    try:
        c.execute(
            "INSERT INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                command_name,
                command_prefix,
                DEFAULT_PERMISSION,
                DEFAULT_DESCRIPTION,
                DEFAULT_USER_COOLDOWN,
                DEFAULT_GLOBAL_COOLDOWN,
                DEFAULT_LAST_USED,
            ),
        )
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        bot.send_privmsg(message.channel, f"There was an error adding the command: {e}")
        conn.close()
        return
    c.execute(
        "INSERT INTO command_values VALUES (?, ?)",
        (
            command_name,
            command_value,
        ),
    )
    bot.send_privmsg(message.channel, f"Successfully added {command_name}.")
    conn.commit()
    conn.close()
