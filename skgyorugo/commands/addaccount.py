from aptbot.bot import Message, Commands, Bot
import sqlite3
import os
import logging
import lol_api.summoner_v4
import ttv_api.users

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler('/var/log/aptbot/logs.log')
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)


PERMISSION = 10
PREFIX = '\\'
DESCRIPTION = "Adds a LoL account to the database. Use: \\addaccount <summoner name> | <twitch name>"
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    summoner_name, twitch_name = msg.split('|')
    summoner = lol_api.summoner_v4.get_summoner_from_name(summoner_name)
    twitch = ttv_api.users.get_users(user_logins=[twitch_name])
    if summoner is None:
        logger.warning(f"Account {summoner_name} wasn't able to be added")
        bot.send_privmsg(message.channel, f"Error, unable to add summoner: {summoner_name}")
        return
    if twitch is None:
        logger.warning(f"Unable to use twitch account {twitch_name}")
        bot.send_privmsg(message.channel, f"Error, unable to use twitch account: {twitch_name}")
        return
    twitch_id = twitch[0].user_id

    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    try:
        c.execute(
            """
            INSERT INTO accounts (
                "puuid",
                "summoner_id",
                "account_id",
                "twitch_id"
            ) VALUES (
                ?, ?, ?, ?
            );
            """,
            (
                summoner.puuid,
                summoner.summoner_id,
                summoner.account_id,
                twitch_id,
            )
        )
    except sqlite3.IntegrityError:
        logger.warning(f"Unable to add account with puuid: {summoner.puuid} and twitch id: {twitch_id}. Account probably already exists")
        bot.send_privmsg(message.channel, f"Account already exists.")
        return
    conn.commit()
    logger.info(f"Successfully added account with puuid: {summoner.puuid} and twitch id: {twitch_id}")
    bot.send_privmsg(message.channel, f"Successfully added account.")
    conn.close()
