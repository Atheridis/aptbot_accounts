import os
import random
import sqlite3
import tools.permissions
import tools.smart_privmsg
from aptbot.bot import Bot, Message, Commands

PATH = os.path.dirname(os.path.realpath(__file__))


def do_command(bot: Bot, message: Message, command_modules: dict):
    conn = sqlite3.connect(os.path.join(PATH, "database.db"))
    c = conn.cursor()

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
            CASE WHEN cooldowns.user_cooldown >= (commands.last_used + commands.global_cooldown) THEN
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
            user_id,
            command,
            prefix,
            user_perm,
        )
    )
    fetched = c.fetchall()
    print(fetched)
    if not fetched:
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
    if value is None:
        command_modules[command].main(bot, message)
    else:
        tools.smart_privmsg.send(bot, message, value)
