from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r"Check who's currently in queue."
USER_COOLDOWN = 30
GLOBAL_COOLDOWN = 15

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
    queue = [x[0] for x in fetched]
    twitch = ttv_api.users.get_users(user_ids=queue)
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching twitch data. Sadge",
            reply=message.tags["id"],
        )
        conn.close()
        return
    queue_names = []
    for twitch_id in queue:
        for twitch_user in twitch:
            if int(twitch_user.user_id) == int(twitch_id):
                queue_names.append(twitch_user.display_name)
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

    queue = queue_names[:queue_size]
    random.shuffle(queue)
    blue_team = queue[: queue_size // 2]
    red_team = queue[queue_size // 2 :]

    bot.send_privmsg(
        message.channel,
        [f"Blue team is: {blue_team}", f"Red team is: {red_team}"],
        reply=message.tags["id"],
    )

    conn.close()
