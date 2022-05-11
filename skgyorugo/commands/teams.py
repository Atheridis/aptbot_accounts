from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import tools.smart_privmsg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r"Check current teams"
USER_COOLDOWN = 30
GLOBAL_COOLDOWN = 15

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        SELECT twitch_id, team FROM lol_queue WHERE team in (0, 1);
        """
    )
    fetched = c.fetchall()
    blue_team = []
    red_team = []
    for user in fetched:
        if user[1] == 0:
            blue_team.append(user[0])
        elif user[1] == 1:
            red_team.append(user[0])
        else:
            bot.send_privmsg(
                message.channel,
                f"Something VERY WEIRD occured. The user with id: {user[0]} is on team {user[1]}, which is neither blue = 0 or red = 1.",
                reply=message.tags["id"],
            )

    users = [x[0] for x in fetched]
    if not users:
        bot.send_privmsg(
            message.channel,
            "No teams have been set yet.",
            reply=message.tags["id"],
        )
        conn.close()
        return

    twitch = ttv_api.users.get_users(user_ids=users)
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching twitch data. Sadge",
            reply=message.tags["id"],
        )
        conn.close()
        return
    blue_team_users = []
    red_team_users = []
    for twitch_user in twitch:
        if int(twitch_user.user_id) in blue_team:
            blue_team_users.append(twitch_user.display_name)
        elif int(twitch_user.user_id) in red_team:
            red_team_users.append(twitch_user.display_name)
        else:
            bot.send_privmsg(
                message.channel,
                f"Something VERY WEIRD occured. The user with id: {twitch_user.user_id} who has the name {twitch_user.display_name} is not on a team.",
                reply=message.tags["id"],
            )

    bot.send_privmsg(
        message.channel,
        [f"Blue team is: {blue_team_users}", f"Red team is: {red_team_users}"],
        reply=message.tags["id"],
    )

    conn.close()
