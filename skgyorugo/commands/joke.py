from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import urllib3
import json

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r""
USER_COOLDOWN = 30
GLOBAL_COOLDOWN = 30

header = {
    "Accept": "application/json",
    "User-Agent": "For my twitch bot [MurphyAI] on https://twitch.tv/ihaspeks",
}


def main(bot: Bot, message: Message):
    http = urllib3.PoolManager()
    r = http.request("GET", "https://icanhazdadjoke.com", headers=header)
    if r.status != 200:
        tools.smart_privmsg.send(
            bot, message, f"Couldn't get a joke Sadge", reply=message.tags["id"]
        )
        return

    data = json.loads(r.data.decode("utf-8"))
    tools.smart_privmsg.send(bot, message, f"{data['joke']}", reply=message.tags["id"])
