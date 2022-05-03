import os
import random
import sqlite3
import tools.permissions
import tools.smart_privmsg
import logging
from aptbot.bot import Bot, Message, Commands

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PATH = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"PATH set to: {PATH}")


def do_command(bot: Bot, message: Message, command_modules: dict):
    db_name_database = "database.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_database))
    c = conn.cursor()
    logger.info(f"connected to database {db_name_database}")

    try:
        replied_message = message.tags["reply-parent-msg-body"]
    except KeyError:
        replied_message = None

    if replied_message:
        command = message.value.split(' ')[1]
    else:
        command = message.value.split(' ')[0]
    prefix = command[0]
    command = command[1:]
    user_id = message.tags["user-id"]
    message_timestamp = int(message.tags["tmi-sent-ts"]) // 1000
    user_perm = tools.permissions.get_permission_from_id(user_id)

    c.execute(
        """
        SELECT
            commands.command,
            value,
            commands.user_cooldown,
            commands.global_cooldown,
            CASE 
                WHEN ? <= 10 THEN
                    0
                WHEN cooldowns.user_cooldown >= (commands.last_used + commands.global_cooldown) THEN
                    cooldowns.user_cooldown
                ELSE
                    (commands.last_used + commands.global_cooldown)
            END AS avail_time

        FROM
            commands
        LEFT JOIN command_values USING (command)
        LEFT JOIN cooldowns ON
        (
            cooldowns.command = commands.command
            AND cooldowns.user_id = ?
        )
        WHERE
            commands.command = ?
            AND prefix = ?
            AND permission >= ?
        """,
        (
            user_perm,
            user_id,
            command,
            prefix,
            user_perm,
        )
    )
    fetched = c.fetchall()
    if not fetched:
        conn.close()
        return

    (_, value,
     command_user_cooldown,
     command_global_cooldown,
     avail_time) = random.choice(fetched)

    if message_timestamp < avail_time:
        bot.send_privmsg(
            message.channel,
            f"The command '{prefix}{command}' is on cooldown. \
            Please wait {int(avail_time - message_timestamp) + 1} seconds."
        )
        conn.close()
        return

    c.execute(
        "REPLACE INTO cooldowns VALUES (?, ?, ?)",
        (
            user_id,
            command,
            command_user_cooldown + message_timestamp,
        )
    )
    c.execute(
        "UPDATE commands SET last_used = ? WHERE command = ?",
        (
            message_timestamp,
            command,
        )
    )
    conn.commit()
    conn.close()
    if value is None:
        command_modules[command].main(bot, message)
    else:
        tools.smart_privmsg.send(bot, message, value)
