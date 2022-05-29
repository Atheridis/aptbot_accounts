from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import tools.smart_privmsg
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
    if random.random() < 0.09:
        q = [
            "https://imgur.com/d5qGioI",
            "https://imgur.com/oaMmxXI",
            "https://imgur.com/4btWipx",
            "https://imgur.com/VvvD8d8",
            "https://imgur.com/v7oflTv",
            "https://imgur.com/MSnBNDz",
            "https://imgur.com/x2pPkvw",
            "https://imgur.com/xZgFcYG",
        ]
        msg = (
            "You wanted to see the queue, but instead you got visited by the Q. monkaW "
        )
        msg += random.choice(q)
        tools.smart_privmsg.send(
            bot,
            message,
            msg,
            reply=message.tags["id"],
        )
        return
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        SELECT twitch_id, priority_queue FROM lol_queue WHERE available = 1 ORDER BY position ASC;
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
    queue_users = []
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
    try:
        queue_size = c.fetchone()[0]
    except TypeError:
        queue_size = 5
        bot.send_privmsg(
            message.channel,
            f"There was an issue fetching the queue size, default set to {queue_size}",
            reply=message.tags["id"],
        )

    play_list = [user.display_name for user in queue_users[1:queue_size]]
    prio_queue = []
    wait_list = []
    for user in queue_users[queue_size:]:
        for fetch in fetched:
            if int(user.user_id) == fetch[0] and fetch[1] == 1:
                prio_queue.append(user.display_name)
            elif int(user.user_id) == fetch[0]:
                wait_list.append(user.display_name)

    if prio_queue:
        msg = f"These people are playing with {message.channel}: {play_list} | These people are in Priority Queue: {prio_queue} | These people are in the Wait List: {wait_list}"
    else:
        msg = f"These people are playing with {message.channel}: {play_list} | These people are in the Wait List: {wait_list}"
    tools.smart_privmsg.send(
        bot,
        message,
        msg,
        reply=message.tags["id"],
    )

    conn.close()
