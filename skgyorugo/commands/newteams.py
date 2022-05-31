from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import random

logger = logging.getLogger(__name__)

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Check who's currently in queue."
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        SELECT twitch_id FROM lol_queue WHERE available = 1 ORDER BY position ASC;
        """
    )
    fetched = c.fetchall()
    queue: list[str] = [x[0] for x in fetched]
    twitch = ttv_api.users.get_users(user_ids=queue)
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching twitch data. Sadge",
            reply=message.tags["id"],
        )
        conn.close()
        return
    queue_users: list[ttv_api.users.User] = []
    for twitch_id in queue:
        for twitch_user in twitch:
            if int(twitch_user.user_id) == int(twitch_id):
                queue_users.append(twitch_user)
                break
        else:
            bot.send_privmsg(
                message.channel,
                f"There was an issue fetching data from the user with id {twitch_id}. They won't be in the list. This is a very weird problem to have occured. Sadge",
                reply=message.tags["id"],
            )
    c.execute(
        """
        SELECT data FROM lol_queue_data WHERE name = 'queuesize';
        """
    )
    fetched = c.fetchone()
    try:
        queue_size = fetched[0]
    except TypeError:
        queue_size = 10
        bot.send_privmsg(
            message.channel,
            f"There was an issue fetching the queue size, default set to {queue_size}",
            reply=message.tags["id"],
        )

    if len(queue_users) < queue_size:
        bot.send_privmsg(
            message.channel,
            f"There aren't enough people in the queue. Current team size is {queue_size} while there are only {len(queue_users)} in queue.",
            reply=message.tags["id"],
        )

    queue_users: list[ttv_api.users.User] = queue_users[:queue_size]
    random.shuffle(queue_users)
    blue_team: list[ttv_api.users.User] = queue_users[: queue_size // 2]
    red_team: list[ttv_api.users.User] = queue_users[queue_size // 2 :]

    c.execute("UPDATE lol_queue SET team = NULL")
    sql = f"UPDATE lol_queue SET team = 0 WHERE twitch_id IN ({(', ?' * (queue_size // 2))[2:]})"
    c.execute(sql, tuple(user.user_id for user in blue_team))
    sql = f"UPDATE lol_queue SET team = 1 WHERE twitch_id IN ({(', ?' * (queue_size - queue_size // 2))[2:]})"
    c.execute(sql, tuple(user.user_id for user in red_team))
    conn.commit()

    blue_team_users: list[str] = [user.display_name for user in blue_team]
    red_team_users: list[str] = [user.display_name for user in red_team]

    bot.send_privmsg(
        message.channel,
        [f"Blue team is: {blue_team_users}", f"Red team is: {red_team_users}"],
        reply=message.tags["id"],
    )

    conn.close()
