from aptbot.bot import Message, Commands, Bot
import sqlite3
import os

PERMISSION = 1
PREFIX = '\\'
DESCRIPTION = ""
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

COMMANDS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(COMMANDS_PATH, "..")


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    command = msg.split(' ')[0]
    command_prefix = command[0]
    command_name = command[1:]

    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()
    c.execute(
        "SELECT value FROM commands WHERE command = ? AND prefix = ?",
        (
            command_name,
            command_prefix,
        )
    )
    command_path = os.path.join(COMMANDS_PATH, f"{command_name}.py")
    hidden_command_path = os.path.join(COMMANDS_PATH, f".{command_name}.py")
    try:
        if not c.fetchone()[0]:
            try:
                os.rename(command_path, hidden_command_path)
            except FileNotFoundError:
                pass
    except TypeError:
        pass

    try:
        c.execute(
            "DELETE FROM commands WHERE command = ? AND prefix = ?",
            (
                command_name,
                command_prefix,
            )
        )
    except sqlite3.IntegrityError:
        bot.send_privmsg(
            message.channel,
            f"The command {command_name} doesn't exist."
        )
    else:
        bot.send_privmsg(
            message.channel,
            f"Successfully removed {command_name}."
        )
    conn.commit()
    conn.close()
