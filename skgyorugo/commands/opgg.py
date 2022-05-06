from aptbot.bot import Message, Commands, Bot
import sqlite3
import os
import logging
from lol_api import spectator_v4
from lol_api import summoner_v4
import ttv_api.users
from tools import smart_privmsg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)


PERMISSION = 99
PREFIX = '?'
DESCRIPTION = "Figures out which LoL Account {channel} is playing on"
USER_COOLDOWN = 20
GLOBAL_COOLDOWN = 15


PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")

def get_streamer_data():
    raise NotImplementedError()

def get_twitch_user_data(twitch_id: int):
    raise NotImplementedError()

def main(bot: Bot, message: Message):
    try:
        twitch_user = message.value.split(' ')[1]
    except IndexError:
        twitch_user = message.tags.get("reply-parent-display-name", message.channel)
        twitch_id = message.tags.get("reply-parent-user-id", ttv_api.users.get_users(user_logins=[message.channel]))
    else:
        twitch_id = ttv_api.users.get_users(user_logins=[twitch_user])

    if not twitch_id:
        logger.warning(f"There was an issue getting twitch data for user {twitch_id}; message id was: {message.tags['id']}")
        smart_privmsg.send(bot, message, "Couldn't retrieve data", reply=message.tags["id"])
        return

    if not isinstance(twitch_id, str):
        twitch_id = int(twitch_id[0].user_id)
    else:
        twitch_id = int(twitch_id)
    db_name_database = "lol_data.db"
    conn = sqlite3.connect(os.path.join(PATH, db_name_database))
    c = conn.cursor()

    c.execute(
        """
        SELECT summoner_id, puuid FROM accounts WHERE twitch_id = ?;
        """,
        (twitch_id,)
    )
    fetched = c.fetchall()

    if not fetched:
        smart_privmsg.send(bot, message, f"No summoners added for {twitch_user}", reply=message.tags["id"])
        return
    
    summoner_names = []
    for summoners in fetched:
        info = spectator_v4.get_spectator_info_from_summoner_id(summoners[0])
        summoner = summoner_v4.get_summoner_from_puuid(summoners[1])
        if summoner:
            summoner_names.append(summoner.name)
        if info:
            break
    else:
        smart_privmsg.send(bot, message, f"{twitch_user} is currently not in game. These are all of their summoners: {summoner_names}", reply=message.tags["id"])
        return

    smart_privmsg.send(bot, message, f"{twitch_user} is currently playing a game on: {summoner_names[-1]}", reply=message.tags["id"])
