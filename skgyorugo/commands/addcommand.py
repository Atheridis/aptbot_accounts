from aptbot.bot import Message, Commands, Bot
import sqlite3
import os

PERMISSION = 1
PREFIX = '\\'
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")

DEFAULT_USER_COOLDOWN = 5
DEFAULT_GLOBAL_COOLDOWN = 0


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    command = msg.split(' ')[0]
    command_prefix = command[0]
    command_name = command[1:]
    command_value = msg = ' '.join(msg.split(' ')[1:])
    if command_prefix != '?':
        bot.send_privmsg(
            message.channel,
            f"{message.nick} you cannot use {command_prefix} as a prefix"
        )
        return

    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                command_name,
                command_prefix,
                99,
                command_value,
                "",
                DEFAULT_USER_COOLDOWN,
                DEFAULT_GLOBAL_COOLDOWN,
            )
        )
    except sqlite3.IntegrityError:
        bot.send_privmsg(
            message.channel,
            f"The command {command_name} already exists."
        )
    except Exception as e:
        bot.send_privmsg(
            message.channel,
            f"There was an error adding the command: {e}"
        )
    else:
        bot.send_privmsg(
            message.channel,
            f"Successfully added {command_name}."
        )
    conn.commit()
    conn.close()
